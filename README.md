# Edelmetall-Kompass & Handy-Melder

- `index.html` – der Kompass (Diagramm, Prognose, Maple Leafs, Melder). Auf GitHub Pages mit Live-Kursen.
- `melder.py` – prüft alle 2 Stunden die Kurse und schickt eine Push-Nachricht über ntfy.
- `melder.json` – deine Melder (Stück + Wunschpreis in €). Im Kompass per Knopf erzeugen.
- `icon.svg`, `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`, `manifest.json` – App-Icon. Auf GitHub Pages im Browser „Zum Startbildschirm hinzufügen“, dann liegt der Kompass wie eine App auf dem Handy.
- `kurs-melder.yml` – die GitHub Action. **Muss unter `.github/workflows/kurs-melder.yml` liegen.**

## Einrichten (einmalig, ca. 10 Minuten)

1. **ntfy-App** aufs Handy (Android/iOS, kostenlos). Dort „Thema abonnieren“ und einen langen, geheimen Namen ausdenken, z. B. `micha-gold-7k3p9x`. Wer den Namen kennt, kann mitlesen – also nicht zu einfach.
2. **Neues GitHub-Repo**, z. B. `Edelmetall-Kompass`, und alle Dateien außer `kurs-melder.yml` hochladen.
3. **Workflow anlegen:** Im Repo „Add file → Create new file“, als Namen `.github/workflows/kurs-melder.yml` tippen (die Schrägstriche legen die Ordner an) und den Inhalt von `kurs-melder.yml` einfügen.
4. **Secret setzen:** Settings → Secrets and variables → Actions → „New repository secret“, Name `NTFY_TOPIC`, Wert = dein Themenname aus Schritt 1.
5. **Testen:** Actions → „Kurs-Melder“ → „Run workflow“. Im Log stehen die Kurse und Preise; ist ein Limit erreicht, kommt die Nachricht aufs Handy.
6. **Optional Pages:** Settings → Pages → Branch `main` → Speichern. Dann läuft der Kompass mit Live-Kursen unter `https://<name>.github.io/Edelmetall-Kompass/`.

## Melder ändern

Im Kompass Melder setzen → „melder.json erzeugen & kopieren“ → im Repo `melder.json` öffnen, Stift-Symbol, alles ersetzen, speichern.

Jede Meldung kommt höchstens einmal pro Tag. Kurse: gold-api.com, Wechselkurs: frankfurter.app (EZB). Die Kaufpreise enthalten ein geschätztes Händler-Aufgeld – echte Preise je nach Händler vergleichen.
