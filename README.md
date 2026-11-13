# Eltako2MQTT

Eltako2MQTT v1.4.0 verbindet Eltako MiniSafe2 mit Home Assistant über MQTT.
Das Add-on liest die im MiniSafe eingerichteten Geräte aus und veröffentlicht ihre Discovery-Konfiguration und Zustände.

## Neu in v1.4.0

- **Nur noch 64 Bit:** Unterstützt werden `amd64` und `aarch64`; `armhf`, `armv7` und `i386` entfallen.
- **Aktuelle Plattform:** Offizielles Home-Assistant-Python-Basisimage mit Python 3.15.2 und Alpine 3.24; aktuelle Pakete der stabilen Alpine-Linie werden beim Build installiert.
- **Abhängigkeiten geprüft:** `aiohttp==3.14.5`, `paho-mqtt==2.2.0` und `PyYAML==6.0.3` sind am 13. November 2026 bereits die neuesten stabilen direkten Abhängigkeiten und bleiben gepinnt.
- **Umfassendere CI:** Python 3.14/3.15, native amd64-/aarch64-Builds, Tests im fertigen Image und vollständiger Containerstart gegen simulierte MiniSafe-/MQTT-Schnittstellen.
- **Bereinigung enthalten:** Ersetzte Altimplementierungen und unnötige Manifest-Rechte entfernt, Dokumentationshistorie korrigiert und zusammengeführt; alte Dokumentations-URLs bleiben erhalten.

**v1.3.0 bleibt die letzte veröffentlichte Version mit 32-Bit-Unterstützung.**
Tag und [Release v1.3.0](https://github.com/Olgrov/eltako2mqtt/releases/tag/v1.3.0) bleiben unverändert; es wird keine fortlaufend gepflegte 32-Bit-Release-Linie eröffnet.
Hinweise für bestehende 32-Bit-Systeme stehen in der [Migration](docs/INSTALLATION.md#32-bit-systeme-und-letzter-legacy-stand).

## Neu in v1.3.0

- **Zustandsrückmeldung:** Die auf dem Testbranch erprobte Implementierung ist jetzt der produktive Einstieg.
- **Rollläden:** Nach erfolgreicher Befehlsannahme erscheint sofort `opening`, `closing` oder `stopped`. Positionen bleiben echte MiniSafe-Rückmeldungen, keine berechneten Zielpositionen.
- **Schalter und Dimmer:** Optimistische Home-Assistant-Bedienung mit anschließender Bestätigung/Korrektur durch reguläres Polling. Die MQTT-Status-Topics enthalten gepollte Werte.
- **Begrenzte Bewegungsannahme:** `eltako.command_feedback_timeout` begrenzt ausstehende Befehle unabhängig von erfolgreichen Polls auf standardmäßig 120 Sekunden. Keine automatischen Wiederholungen.
- **Schonendes Polling:** Standard 30 Sekunden, serialisierte MiniSafe-HTTP-Zugriffe und keine zusätzliche `GetStates`-Abfrage nach einem Befehl.
- **Robuste Helligkeit:** Ungültige Dimmerwerte überschreiben die letzte gültige Helligkeit nicht mit 0.
- **MQTT-Bibliothek:** `paho-mqtt` 2.2.0 aus [PR #25](https://github.com/Olgrov/eltako2mqtt/pull/25); VERSION2-Callbacks bleiben erhalten.

Details und Upgrade-Hinweise stehen in den [Release Notes](docs/RELEASE_NOTES.md).
FSR14M-Leistungsmessung ist nicht Teil dieses Releases.

## Unterstützte Geräte

- **Rollläden/Jalousien:** `eltako_blind`, `eltako_tf_blind`, Positionssteuerung und Öffnen/Schließen/Stop.
- **Schalter:** `eltako_switch`, `eltako_tf_switch`, FSR14, FSR14M-2x, FSR14SSR, F4SR14-LED und FAE14; `on`, `off`, `toggle`.
- **Dimmer:** `eltako_dimmer`, `eltako_tf_dimmer`; `on`, `off` und Helligkeit 0–255.
- **Wetterstationen:** `eltako_weather`; Temperatur, Wind, Regen und Beleuchtungsstärke.
- **Rauchmelder:** Gerätetypen mit `tf_smoke`, unter anderem FRWB; Rauchalarm und Temperatur.

Mehrkanalige Geräte erscheinen entsprechend den vom MiniSafe gemeldeten SIDs.
RSSI wird als MQTT-Wert in Prozent veröffentlicht, nicht als automatisch entdeckter dBm-Sensor.

## Installation und Update

1. In Home Assistant unter Einstellungen → Add-ons → Add-on Store → Repositories das Repository `https://github.com/Olgrov/eltako2mqtt` hinzufügen.
2. Auf einem unterstützten 64-Bit-System Eltako2MQTT installieren bzw. auf 1.4.0 aktualisieren und die Konfiguration speichern.
3. MQTT-Integration/Broker einrichten und das Add-on starten.
4. Im Log `Eltako2MQTT 1.4.0; poll interval=30s; feedback timeout=120s` sowie die Discovery-Meldungen prüfen.

Bestehende Produktionsinstallationen behalten Slug `eltako2mqtt`, MQTT-Client-ID, Command-Topics und Discovery-IDs.
Ein eventuell installiertes Test-Add-on muss vor dem Start gestoppt und sein Autostart deaktiviert werden, da beide Varianten dieselben Geräte ansteuern.

## Konfiguration

```yaml
eltako:
  host: "192.168.1.100"
  password: "MINISAFE_PASSWORT"
  poll_interval: 30
  command_feedback_timeout: 120
mqtt:
  host: "core-mosquitto"
  port: 1883
  username: "mqtt_user"
  password: "MQTT_PASSWORT"
  client_id: "eltako2mqtt"
logging:
  level: "INFO"
```

- **Pflichtfelder:** `eltako.host`, `eltako.password`, `mqtt.host`.
- **Polling:** `poll_interval` ist optional, Standard 30 Sekunden, Add-on-Bereich 1–300. Werte unter 30 Sekunden sind aus Stabilitätsgründen nicht empfohlen und erzeugen eine Warnung; bestehende kleinere Werte werden nicht automatisch angehoben.
- **Feedback-Timeout:** Optional, Standard 120 Sekunden, Add-on-Bereich 30–900. Längste Fahrzeit plus Rückmeldeverzögerung berücksichtigen; kein Ersatz für das Pollingintervall.
- **MQTT:** Port standardmäßig 1883, Client-ID `eltako2mqtt`. Benutzername und Passwort bei authentifiziertem Broker gemeinsam angeben.
- **Logging:** `DEBUG`, `INFO`, `WARNING`, `ERROR`; Standard `INFO`. Zugangsdaten nicht in Fehlerberichte übernehmen.

## MQTT und Positionsskalen

Alle Befehle gehen an `eltako/{SID}/set`.
Rollladenbefehle verwenden die Home-Assistant-Skala, Statuswerte hingegen die unveränderte MiniSafe-Skala.

| Oberfläche | Geschlossen | Offen |
| --- | --- | --- |
| Home Assistant / numerischer MQTT-Befehl | 0 | 100 |
| MiniSafe / MQTT `eltako/{SID}/state` | 100 | 0 |

```bash
# Rollladen öffnen; numerisch entspricht dies 100
mosquitto_pub -h BROKER -t eltako/01/set -m open
# Rollladen schließen; numerisch entspricht dies 0
mosquitto_pub -h BROKER -t eltako/01/set -m 0
# Dimmer: ungefähr 50 Prozent, Skala 0–255
mosquitto_pub -h BROKER -t eltako/13/set -m 128
# Alle Gerätezustände beobachten
mosquitto_sub -h BROKER -v -t 'eltako/#'
```

`eltako/{SID}/movement` enthält die Bewegungsanzeige, `.../state` die Position bzw. den Schaltzustand und `.../brightness` die Dimmerhelligkeit.
Ein `.../pos`-Topic existiert nicht; vollständige Topics und Beispiele stehen in der [MQTT-Referenz](docs/MQTT_COMMANDS.md).

## Grenzen und Diagnose

Eine angenommene Fahrtrichtung ist kein gemessener Motorzustand.
Auch ein Timeout oder eine Positionsprobe nach Stop beweist weder Motorstillstand noch Befehlsfehlschlag.

MiniSafe kann Positionen erst nach mehreren Polls aktualisieren.
Bei verzögerter Rückmeldung nicht schneller pollen, sondern die Logs und bei Bedarf den Feedback-Timeout prüfen.
Das Add-on hat kein Availability-/Last-Will-Topic; retained Zustände können nach einem Ausfall veraltet sein.
Die Rauchmelderintegration ersetzt keine zertifizierte Alarmierung.

## Dokumentation und Entwicklung

- **Einstieg:** [Dokumentationsindex](docs/DOCUMENTATION.md) und [Installation](docs/INSTALLATION.md).
- **Bedienung:** [MQTT-Referenz](docs/MQTT_COMMANDS.md) und [Feedback-Tests](docs/TESTING_OPTIMISTIC_STATE.md).
- **Entwicklung:** [Architektur/API](docs/API.md), [Changelog](CHANGELOG.md) und [Release Notes](docs/RELEASE_NOTES.md).
- **Support:** [Issues](https://github.com/Olgrov/eltako2mqtt/issues).

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Python 3.15 ist die Container-Laufzeit; `requirements.txt` ist die gemeinsame Abhängigkeitsquelle für lokale Installation und Docker.
Enthalten sind `aiohttp==3.14.5`, `paho-mqtt==2.2.0` und `PyYAML==6.0.3`.
Die direkten Versionen wurden gegen [aiohttp](https://pypi.org/project/aiohttp/), [Paho](https://pypi.org/project/paho-mqtt/) und [PyYAML](https://pypi.org/project/PyYAML/) geprüft.
Unterstützte Architekturen sind ausschließlich aarch64 und amd64; automatisierte Tests ersetzen keinen physischen MiniSafe-Test.

<a name="wartungsstand-auf-main"></a>

## Versions- und Plattformstand

Die bisher separat vorbereitete Bereinigung und die Basis-Migration sind in v1.4.0 zusammengeführt.
Der [Changelog](CHANGELOG.md#140---2026-11-13) dokumentiert den Umfang; historische Versionsabschnitte beschreiben weiterhin ihre damalige Plattform und nicht den aktuellen Support.
