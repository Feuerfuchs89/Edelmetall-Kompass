#!/usr/bin/env python3
"""Edelmetall-Melder: prüft Gold-/Silberkurse und schickt eine Push-Nachricht über ntfy.

Läuft per GitHub Action (kurs-melder.yml) alle 2 Stunden.
Einstellungen stehen in melder.json, das ntfy-Thema im Repo-Secret NTFY_TOPIC.
Test ohne Internet:  python melder.py --test
"""
import json, os, sys, datetime, urllib.request

OZ = 31.1035
HIER = os.path.dirname(os.path.abspath(__file__))
STATUS = os.path.join(HIER, "melder-status.json")

# id: (Name, Metall, Feingewicht in g, geschätztes Aufgeld inkl. Steuer) – gleich wie im Kompass
STUECKE = {
    "ml-g120": ("Gold Maple Leaf 1/20 oz", "gold", OZ / 20, 0.20),
    "ml-g110": ("Gold Maple Leaf 1/10 oz", "gold", OZ / 10, 0.10),
    "ml-g14":  ("Gold Maple Leaf 1/4 oz", "gold", OZ / 4, 0.07),
    "ml-g12":  ("Gold Maple Leaf 1/2 oz", "gold", OZ / 2, 0.05),
    "ml-g1":   ("Gold Maple Leaf 1 oz", "gold", OZ, 0.03),
    "ml-s1":   ("Silber Maple Leaf 1 oz", "silver", OZ, 0.27),
    "g1":   ("Goldbarren 1 g", "gold", 1, 0.15),
    "g2":   ("Goldbarren 2 g", "gold", 2, 0.10),
    "g25":  ("Goldbarren 2,5 g", "gold", 2.5, 0.09),
    "g5":   ("Goldbarren 5 g", "gold", 5, 0.065),
    "g10":  ("Goldbarren 10 g", "gold", 10, 0.045),
    "g20":  ("Goldbarren 20 g", "gold", 20, 0.04),
    "s10":  ("Silberbarren 10 g", "silver", 10, 0.60),
    "s50":  ("Silberbarren 50 g", "silver", 50, 0.40),
    "s100": ("Silberbarren 100 g", "silver", 100, 0.33),
    "s250": ("Silberbarren 250 g", "silver", 250, 0.29),
    "s500": ("Silberbarren 500 g", "silver", 500, 0.27),
    "s1k":  ("Silberbarren 1 kg", "silver", 1000, 0.25),
}


def hole_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "edelmetall-melder/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def kurse(cfg):
    if "--test" in sys.argv:
        return 3950.0, 49.0, 0.89
    gold = float(hole_json("https://api.gold-api.com/price/XAU")["price"])
    silber = float(hole_json("https://api.gold-api.com/price/XAG")["price"])
    try:
        fx = float(hole_json("https://api.frankfurter.app/latest?from=USD&to=EUR")["rates"]["EUR"])
    except Exception:
        fx = float(cfg.get("usd_in_eur", 0.89))
    return gold, silber, fx


def preis_eur(stueck_id, gold, silber, fx):
    name, metall, gramm, aufgeld = STUECKE[stueck_id]
    usd_oz = gold if metall == "gold" else silber
    return gramm * usd_oz / OZ * fx * (1 + aufgeld)


def eur(v):
    s = f"{v:,.2f}" if v < 100 else f"{v:,.0f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def senden(topic, titel, text, tags="moneybag"):
    if "--test" in sys.argv or not topic:
        print(f"[nur Test] {titel}: {text}")
        return
    req = urllib.request.Request(
        "https://ntfy.sh/" + topic,
        data=text.encode("utf-8"),
        headers={"Title": titel, "Tags": tags, "Priority": "high"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=20).read()


def main():
    with open(os.path.join(HIER, "melder.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    try:
        with open(STATUS, encoding="utf-8") as f:
            status = json.load(f)
    except Exception:
        status = {}
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    heute = datetime.date.today().isoformat()

    gold, silber, fx = kurse(cfg)
    ratio = gold / silber
    print(f"Gold {gold:.0f} $  Silber {silber:.2f} $  Ratio {ratio:.1f}  1 $ = {fx:.4f} €")

    meldungen = []
    for a in cfg.get("melder", []):
        sid, ziel = a["stueck"], float(a["wunschpreis"])
        if sid not in STUECKE:
            print("Unbekanntes Stück:", sid)
            continue
        p = preis_eur(sid, gold, silber, fx)
        name = STUECKE[sid][0]
        print(f"  {name}: ca. {eur(p)} (Wunsch {eur(ziel)})")
        schluessel = f"{sid}@{ziel:g}"
        if p <= ziel and status.get(schluessel) != heute:
            meldungen.append(f"Dein Wunschpreis ist erreicht: {name} jetzt ca. {eur(p)} (Limit {eur(ziel)}).")
            status[schluessel] = heute

    if cfg.get("kaufsignal", True):
        hoch, tief = cfg.get("ratio_silber_ab", 80), cfg.get("ratio_gold_unter", 60)
        sig = None
        if ratio > hoch:
            sig = f"Ampel grün: Silber Maple Leafs sind im Vergleich zu Gold gerade billig (1 Unze Gold = {ratio:.0f} Unzen Silber). Guter Zeitpunkt zum Nachkaufen."
        elif ratio < tief:
            sig = f"Ampel grün: Gold Maple Leafs sind im Vergleich zu Silber gerade billig (1 Unze Gold = {ratio:.0f} Unzen Silber). Guter Zeitpunkt zum Nachkaufen."
        if sig and status.get("signal") != heute:
            meldungen.append(sig)
            status["signal"] = heute

    if meldungen:
        senden(topic, "Edelmetall-Melder", "\n".join(meldungen))
    else:
        print("Nichts zu melden.")

    if "--test" not in sys.argv:
        with open(STATUS, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=1)


if __name__ == "__main__":
    main()
