<a name="feedback-testplan-für-eltako2mqtt-v130"></a>

# Feedback-Testplan für Eltako2MQTT v1.4.0

Die zuvor experimentelle Zustandsrückmeldung läuft jetzt im produktiven Add-on.
Der Dateiname bleibt für vorhandene Verweise erhalten; es gibt keinen separaten Test-Launcher in diesem Release.

## Konfiguration und Testvorbereitung

```yaml
eltako:
  poll_interval: 30
  command_feedback_timeout: 120
logging:
  level: DEBUG
```

Diese Werte in die vorhandene Konfiguration mit Host und Zugangsdaten eintragen.
Das produktive Add-on auf amd64 oder aarch64 neu bauen/aktualisieren, dann starten und die Logzeile `Eltako2MQTT 1.4.0; poll interval=30s; feedback timeout=120s` prüfen.
Vorher jedes experimentelle Add-on stoppen und dessen Autostart deaktivieren; unterschiedliche Client-IDs verhindern keine doppelten Gerätebefehle.

## Praktische Regressionen

1. Schließen-Taste und Slider 0 Prozent: nach Annahme `closing`, MiniSafe-Rohziel 100.
2. Öffnen-Taste und Slider 100 Prozent: `opening`, Rohziel 0.
3. Alte Position über mehrere Polls: echte Position bleibt sichtbar, angenommene Fahrtrichtung bleibt bis Ziel/Timeout bestehen.
4. Teilpositionen und rasche Richtungswechsel: neuester akzeptierter Befehl bestimmt die Annahme; Gegenbewegung ändert nur die gemeldete Position.
5. Stop: sofort `stopped`; nächster Poll liefert die tatsächliche Position ohne unbelegte Motorbestätigung.
6. Ziel erreicht: Abschluss beim passenden Poll, nicht erst am Timeout. Ein Prozentpunkt Toleranz verändert den gemeldeten Rohwert nicht.
7. Externe Bedienung: ohne Pending wird Richtung aus Positionsdifferenzen abgeleitet; keine kontinuierliche Bewegungserfassung.
8. Fehlende Rückmeldung: unabhängiger Timeout beendet die Annahme ohne Zusatzabfrage oder Befehlswiederholung.
9. Dimmer ohne gültigen Level: kein künstlicher Wert 0; Ein-/Aus und RSSI bleiben erhalten. Bei gültigem Level setzt Helligkeitspublikation wieder ein.
10. Schalter/Dimmer: UI reagiert optimistisch, Status-Topics bleiben regulär gepollt.
11. Wetter/Rauch: bestehende Discovery-IDs und Topics bleiben erhalten; RSSI ist Prozent und kein separater Discovery-Sensor.
12. Neustart/Migration: keine doppelten Entitäten oder parallelen Instanzen; optionale Timeout-Vorgabe bleibt wirksam.

`opening`/`closing`, unveränderte Positionsproben und Timeout beweisen keinen Motorzustand.
Physische Bewegung und Rückmeldeverzögerung können aus diesen Logs allein nicht getrennt bestimmt werden.

## Debug-Logs

- **Start:** `Eltako2MQTT 1.4.0; poll interval=...; feedback timeout=...`.
- **Tracking:** `Command tracking ... raw_target=... movement=...`.
- **Ersatz:** `Command superseded ...`.
- **Polling:** `GetStates started; interval_since_previous=...` und `GetStates completed ...`.
- **Abgleich:** `Cover poll ... raw_pos=... ha_pos=... movement=... assumed_motion=...`.
- **Timeout:** `Command feedback timeout ... target not confirmed, no command retry`.
- **Stop:** `Position observed after accepted stop ... motor stop not independently verified`.

GetStates-Startabstände müssen mindestens `poll_interval` betragen, auch nach dem ersten Startpoll.
Befehle dürfen keinen zusätzlichen GetStates-Aufruf auslösen; längere HTTP-Requests dürfen wegen des Locks keine parallelen MiniSafe-Zugriffe erzeugen.

## Automatisierte Tests

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q eltako2mqtt.py bridge_base.py state_feedback.py tests
python tools/check_links.py
bash -n run.sh
```

Die Feedback-Tests simulieren HTTP/MQTT und verzögerte Rückmeldungen.
Produktionsverträge prüfen zusätzlich Startpfad, Docker-COPY-Quellen, Versionskonsistenz, tatsächliche Paho-VERSION2-Callbacks und die Konfigurationsübertragung mit Sonderzeichen.
Die CI prüft Python 3.14/3.15 und baut Images für amd64 und aarch64 auf nativen Runnern.
Im Image werden die Abhängigkeiten, die Unittests und der vollständige Standard-Containerstart mit simuliertem MiniSafe und MQTT getestet; ein Test gegen echte Hardware ist dies nicht.
Der zusätzliche Container-Smoke-Test verwendet nur gegen seine Loopback-Fakes `poll_interval: 1`; die Empfehlung für echte MiniSafe-Geräte bleibt mindestens 30 Sekunden.
Ein CI-Vertrag prüft, dass Tag v1.3.0 weiterhin auf dem unveränderten letzten 32-Bit-Release steht; es gibt keine v1.4.0-Builds für armhf, armv7 oder i386.
Der Offline-Linkchecker prüft lokale Ziele und Überschriftenanker; externe HTTP-Ziele und die veröffentlichte Pages-Ausgabe sind davon getrennte Live-Prüfungen.
