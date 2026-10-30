# Testbranch: Zustandsrückmeldung

## Version 1.2.5-test.3

Testversion auf `test/optimistic-state-feedback`; kein produktives Release. `main` und `eltako2mqtt.py` bleiben unverändert.

- Home Assistant sendet 0 = geschlossen, 100 = offen. MiniSafe verwendet die umgekehrte Rohposition: 0 = offen, 100 = geschlossen. Steuerbefehle und MQTT-Gerätetopics bleiben unverändert.
- Nach erfolgreicher Befehlsannahme erscheint `opening`, `closing` oder bei Stop `stopped`.
- Alte, unveränderte oder gegenläufige Rückmeldungen beenden/überschreiben eine noch ausstehende Fahrtrichtung nicht vorzeitig. Neue akzeptierte Befehle ersetzen die vorherige Annahme.
- Erreicht die gültige Rückmeldung das erwartete Ziel (Toleranz 1 Prozentpunkt), endet die Bewegungsannahme beim verarbeitenden Poll. Für Teilpositionen wird `stopped` angezeigt.
- **Jede gültige Positionsrückmeldung wird unverändert veröffentlicht.** Nur die Bewegungsanzeige wird vorübergehend angenommen. Keine simulierten Positionen und keine zusätzliche `GetStates`-Abfrage nach Befehlen.
- `opening`/`closing` sind keine gemessenen Motorzustände. Eine Positionsrückmeldung nach Stop bestätigt keinen unabhängigen Motorstillstand; das Log unterscheidet dies nun ausdrücklich.
- Der unabhängige Timeout begrenzt die Annahme auch bei ausbleibenden erfolgreichen Polls. Danach erscheint eine Warnung und die Anzeige fällt auf den letzten bekannten Positionszustand zurück. Das beweist weder Stillstand noch Befehlsfehlschlag. Kein automatischer Retry.
- Fehlende/ungültige Dimmerhelligkeit veröffentlicht keinen Ersatzwert 0. Gültige Ein-/Aus-Zustände und RSSI werden weiterhin veröffentlicht. Eine Warnung mit SID erscheint einmal pro Fehlerphase; der letzte gültige Helligkeitswert bleibt erhalten.
- Covers bleiben `optimistic: false`; Dimmer und Schalter bleiben optimistisch. Ein gemeinsamer Lock serialisiert MiniSafe-HTTP-Zugriffe. GetStates-Startabstände bleiben mindestens `poll_interval`, auch beim Start.

## Konfiguration

Im vorhandenen `eltako`-Block ergänzen; vorhandene Zugangsdaten beibehalten:

```yaml
eltako:
  poll_interval: 30
  command_feedback_timeout: 120
logging:
  level: DEBUG
```

`command_feedback_timeout` ist optional (Default 120 Sekunden, Add-on-Schema 30–900 Sekunden). Es ist **nicht das Pollingintervall**. Den Wert an die längste reale Fahrzeit zuzüglich Rückmeldeverzögerung anpassen. Die Pollingrate nicht verkürzen, um verspätete MiniSafe-Positionswerte zu kaschieren. Aus den Logs allein lassen sich Fahrt und Rückmeldeverzögerung nicht trennen.

## Aktualisieren

```bash
cd /addons/eltako2mqtt-experimental
git pull --ff-only origin test/optimistic-state-feedback
```

Lokale Add-ons im Store neu laden und **auf 1.2.5-test.3 aktualisieren/neu bauen**. Ein Neustart des alten Images genügt nicht. Keine Entitäten löschen; Discovery wird beim Start erneut veröffentlicht.

Das produktive Add-on während des Tests stoppen: Beide Varianten verwenden dieselben MQTT-Command-Topics und Discovery-IDs. Nicht parallel betreiben.

## Regressionstest

1. Schließen-Taste und Slider 0 %: nach Annahme `wird geschlossen`, MiniSafe-Rohziel 100.
2. Öffnen-Taste und Slider 100 %: `wird geöffnet`, Rohziel 0.
3. Alte Position über mehrere Polls: echte Position bleibt sichtbar, angenommene Fahrtrichtung bleibt bis Ziel/Timeout bestehen.
4. Teilpositionen und rasche Richtungswechsel: neuester akzeptierter Befehl bestimmt die angenommene Richtung; verspätete Gegenbewegung ändert nur die gemeldete Position.
5. Stop: sofort `stopped`; nächster Poll liefert die tatsächliche Position ohne unbelegte Motorbestätigung.
6. Ziel erreicht: sofortiger Abschluss am verarbeitenden Poll, kein Warten bis Timeout.
7. Externe Bedienung: ohne ausstehenden Befehl wird die Richtung aus aufeinanderfolgenden Positionswerten abgeleitet; das ist keine kontinuierliche Bewegungserfassung.
8. Fehlende Rückmeldung: Timeout beendet die Annahme ohne zusätzliche Hardwareanfrage oder Wiederholung des Steuerbefehls.
9. Dimmer mit fehlender Helligkeit: kein künstlicher Wert 0, Warnung mit SID, Wiederaufnahme bei gültigem Wert.

## Debug-Logs

- `Experimental bridge 1.2.5-test.3; poll interval=30s; feedback timeout=120s` identifiziert das neue Image. Die Basisklasse kann zuvor ihren alten Default-Timeout loggen; die experimentelle Startzeile nennt den wirksamen Wert.
- `Command tracking ... raw_target=... movement=...` zeigt das Rohziel.
- `Command superseded ...` erklärt ersetzte Befehle.
- `GetStates started; interval_since_previous=...` und `GetStates completed ...` zeigen Startabstände und Antwortzeiten.
- `Cover poll ... raw_pos=... ha_pos=... movement=... assumed_motion=...` trennt reale Position und Annahme.
- `Command feedback timeout ... target not confirmed, no command retry` beendet lediglich die Annahme.
- `Position observed after accepted stop ... motor stop not independently verified` ist ausdrücklich keine Motorbestätigung.

## Automatisierte Tests

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile eltako2mqtt.py eltako2mqtt_experimental.py tests/test_experimental_state.py
bash -n run-experimental.sh
```

Die Tests verwenden simulierte HTTP-/MQTT-Schnittstellen und nachgestellte Log-Szenarien, keine echte Hardware. Container-Build, MiniSafe2 und Home-Assistant-Frontend müssen zusätzlich praktisch geprüft werden.
