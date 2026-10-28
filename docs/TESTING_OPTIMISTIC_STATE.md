# Testbranch: Zustandsrückmeldung

## Version 1.2.5-test.2

Diese Testversion korrigiert die Richtungsanzeige und die an den Pending-Timeout gekoppelte Bewegungsanzeige aus test.1. `main` und die produktive Bridge bleiben unverändert.

- Home Assistant sendet mit dem vorhandenen `set_position_template` seine eigene Prozentposition: 0 = geschlossen, 100 = offen.
- Die Bridge sendet unverändert `moveTo(100 - HA-Position)` an den MiniSafe2. Rohstatus und Pending-Ziel verwenden 0 = offen, 100 = geschlossen.
- Ein Schließbefehl meldet nach erfolgreicher Annahme `closing`, ein Öffnungsbefehl `opening` und ein Stop-Befehl `stopped`.
- Covers verwenden `optimistic: false`, damit Home Assistant nicht sofort eine erreichte Endposition simuliert. Dimmer und Schalter bleiben optimistisch.
- Jeder erfolgreiche reguläre Poll veröffentlicht die echte Position. Die Bewegungsanzeige folgt erreichten Zielen oder der Änderung zwischen zwei Rückmeldungen, nicht dem 90-Sekunden-Pending-Timeout. Eine unveränderte Position ohne neue Bewegungsbestätigung beendet die angenommene Bewegung; nur unmittelbar nach dem Befehl gilt eine zweisekündige Grace Period.
- Aus diskreten Positionswerten lässt sich Bewegung nicht lückenlos nachweisen. `opening`/`closing` aus dem Befehl sind zunächst eine Annahme, kein unabhängiger Motorsensor. Ein unveränderter MiniSafe-Cache kann daher keine weiterhin laufende Fahrt bestätigen.
- Pending-Timeouts dienen nur Diagnosezwecken und sperren keine Statuspublikation.
- Keine zusätzlichen `GetStates` nach Befehlen. Startabstände der Abfragen betragen mindestens `poll_interval`, auch beim Start. Wartezeiten und Timeouts können den Abstand verlängern, niemals eine garantierte Hardware-Reaktionszeit erzwingen.

## Aktualisieren

Für eine lokale Installation unter `/addons/eltako2mqtt-experimental`:

```bash
cd /addons/eltako2mqtt-experimental
git pull --ff-only origin test/optimistic-state-feedback
```

Danach im Add-on-Store die lokalen Add-ons neu laden beziehungsweise nach Updates suchen. **Eltako2MQTT Experimental auf 1.2.5-test.2 aktualisieren/neu bauen und starten. Ein reiner Neustart des alten Images genügt nicht.** Keine Entitäten löschen; die Discovery wird beim Start erneut veröffentlicht.

Das produktive Add-on während des Tests stoppen: Beide Varianten verwenden dieselben MQTT-Command-Topics und Discovery-IDs. `poll_interval: 30` und `logging.level: DEBUG` einstellen.

## Regressionstest

1. Vollständig offenen Rollladen über Schließen-Taste schließen: nach Befehlsannahme `wird geschlossen`.
2. Dasselbe über den Positionsslider auf 0 % ausführen: ebenfalls `wird geschlossen`, Pending-Rohziel 100.
3. Öffnen-Taste und Slider auf 100 % testen: `wird geöffnet`, Pending-Rohziel 0.
4. Teilpositionen in beide Richtungen und einen Stop-Befehl testen.
5. Am nächsten regulären erfolgreichen Poll muss der gelieferte Rohstatus veröffentlicht werden; ein erreichtes Ziel beendet die Bewegungsanzeige sofort, ohne auf den Pending-Timeout zu warten.
6. Parallel `eltako/+/state` und `eltako/+/movement` beobachten und mit `GetStates`-Logs vergleichen. Keine zusätzlichen Statusabfragen erzwingen.
7. Externe Bedienung testen; Positionsänderungen müssen beim nächsten Poll ankommen.
8. Bei unverändertem oder ausbleibendem Rohstatus die Logs sichern: Das Add-on kann keine neue reale Position ermitteln, die der MiniSafe nicht liefert.

## Debug-Logs

- `Experimental bridge 1.2.5-test.2; poll interval=30s` bestätigt das neue Image.
- `Command tracking ... raw_target=... movement=...` zeigt die Richtungszuordnung.
- `GetStates started; interval_since_previous=...` zeigt die tatsächlichen Startabstände.
- `GetStates completed in ...; devices=...` zeigt erfolgreiche Antworten.
- `Cover poll ... raw_pos=... previous=... movement=... pending_age=...` trennt MiniSafe-Rückmeldung und UI-Bewegung.
- `Command not confirmed ...` ist eine Diagnose, keine Wartebedingung für die UI.

## Automatisierte Tests

```bash
python3 -m unittest discover -s tests -v
```

Die Tests verwenden simulierte HTTP- und MQTT-Schnittstellen. Ein realer MiniSafe2, Home-Assistant-Frontend und Containerbuild müssen zusätzlich praktisch geprüft werden.
