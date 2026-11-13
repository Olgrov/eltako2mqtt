# Architektur und Entwicklerreferenz für v1.3.0

Eltako2MQTT ist eine Python-Bridge mit einer asynchronen MiniSafe-HTTP-Seite und einem Paho-MQTT-Netzwerkthread.
Es gibt keinen eigenen HTTP-Server und keine öffentliche REST-API der Bridge.

## Produktiver Aufbau

- **`eltako2mqtt.py`:** CLI-Einstieg `python3 eltako2mqtt.py CONFIG.yaml`; exportiert `EltakoMiniSafe2Bridge` als Alias der produktiven `StateFeedbackBridge`.
- **`bridge_base.py`:** Gemeinsame Geräteerkennung, MiniSafe-Befehlsübersetzung, MQTT-VERSION2-Callbacks, Sensorpublikation und Discovery.
- **`state_feedback.py`:** Produktive Ableitung mit Pending-Tracking, Watchdog, HTTP-Lock, Poll-Scheduling, validierter Helligkeit und Bewegungsanzeige.
- **`run.sh`:** Prüft Pflichtoptionen und serialisiert Supervisor-JSON sicher nach YAML, inklusive optionalem Timeout.
- **`requirements.txt`:** Einzige Abhängigkeitsquelle auch für das Docker-Image.
- **`tests/`:** Unittest-Regressionen und Paketierungs-/Konfigurationsverträge.

Es wird kein experimentelles Modul importiert oder gestartet.
Die Basisklasse alleine ist kein alternativer unterstützter Produktionspfad.

## Datenfluss und Methoden

`on_mqtt_message()` plant Coroutinen threadsicher auf dem Bridge-Eventloop ein.
`handle_device_command(sid, command)` validiert und übersetzt einen Befehl, wartet auf den gemeinsamen Lock und sendet genau einen `SendSC`-Request.
Nur HTTP 200 mit `{XC_SUC}` gilt als Befehlsannahme und erzeugt Pending-Tracking.

- **`_track_pending()`:** Speichert Befehl, erwartete Teilzustände, Zeitstempel und gegebenenfalls Bewegungsannahme pro SID.
- **`_pending_matches()`:** Vergleicht gepollte Zustände; numerische Werte müssen endlich, im Bereich 0–100 und höchstens einen Prozentpunkt vom Ziel entfernt sein.
- **`_reconcile_pending()`:** Löst passende oder abgelaufene Befehle auf und leitet die Bewegungsanzeige ab, bevor der neue echte Zustand gecacht wird.
- **`_pending_watchdog()`:** Beendet die Annahme auch bei ausbleibenden erfolgreichen Polls; alte Timer dürfen Ersatzbefehle nicht löschen.
- **`_clear_pending()`:** Entfernt Tracking und beendet den zugehörigen Timer.
- **`fetch_device_states()`:** Serialisiert Requests und hält mindestens `poll_interval` zwischen `GetStates`-Starts ein, auch beim Start.
- **`_validate_device_states()`:** Erwartet eine Liste; verwirft fehlerhafte Einträge ohne SID/String-Typ oder mit ungültigem State-Container.
- **`publish_device_state()`:** Veröffentlicht reale Rohzustände; ungültige Coverpositionen und Dimmerhelligkeiten werden nicht durch erfundene Werte ersetzt.
- **`publish_discovery()`:** Konfiguriert Cover mit Bewegungs-/Positions-Topics, Schalter/Dimmer optimistisch und erhält Sensor-Discovery.

Der Lock bleibt beim Warten auf den nächsten Polltermin frei.
Ein Befehl löst keinen zusätzlichen `GetStates`-Request aus; lange aktive HTTP-Requests können Befehle jedoch verzögern.
Timeouts werden beim Shutdown abgebrochen und eingesammelt.

## MiniSafe-Protokoll

```text
http://HOST/command?XC_FNC=GetStates&XC_PASS=URL_ENCODED_PASSWORD
http://HOST/command?XC_FNC=SendSC&type=ENOCEAN&address=ADR&data=COMMAND&XC_PASS=URL_ENCODED_PASSWORD
```

`GetStates` erwartet `{XC_SUC}` gefolgt von einer JSON-Geräteliste.
Geräte enthalten unter anderem `sid`, `data`, `adr` und `state`; je nach Gerät etwa `pos`, `state`, `level`, `rssiPercentage`, Wetter- oder Rauchwerte.
Diese Schnittstelle ist MiniSafe-spezifisch und nicht die API eines Servers in diesem Add-on.

Coverbefehle werden genau einmal invertiert: MQTT 0=geschlossen → `moveTo100`, MQTT 100=offen → `moveTo0`.
Der publizierte Coverstatus bleibt dagegen unverändert in der MiniSafe-Skala 0=offen, 100=geschlossen.
Dimmer-Numerik ist immer 0–255 und wird auf 0–100 umgerechnet; 0 sendet `off`.
Alle Topicverträge stehen in der [MQTT-Referenz](MQTT_COMMANDS.md).

## Semantik und Grenzen

- **Befehlsannahme:** `{XC_SUC}` bestätigt nicht, dass das physische Gerät bereits den Zielzustand erreicht hat.
- **Coverbewegung:** Kann aus einem angenommenen Befehl oder Positionsdifferenzen stammen; kein Motor-Running-Sensor.
- **Stop:** Eine gültige Probe nach Stop beendet Tracking, wird aber ausdrücklich nicht als unabhängige Motorbestätigung geloggt.
- **Timeout:** Standard 120 Sekunden, kein Retry, keine Fahrtabschaltung und keine erfundene Zielposition.
- **Optimismus:** Schalter/Dimmer nutzen die Home-Assistant-UI; Status-Topics bleiben gepollt. Cover nutzen `optimistic: false`.
- **Helligkeit:** Nicht-endliche, boolesche, fehlende oder außerhalb 0–100 liegende Level werden ignoriert; Warnungen werden pro Fehlerphase/SID begrenzt.
- **Sicherheit:** HTTP ohne TLS, MQTT ohne TLS-Konfiguration, kein Availability-/LWT-Vertrag. Keine MiniSafe-URLs mit Passwort in Fehlerberichte übernehmen.

## Abhängigkeiten und Kompatibilität

Python 3.11 ist die Container-Laufzeit mit `aiohttp==3.14.5`, `paho-mqtt==2.2.0` und `PyYAML==6.0.3`.
Paho nutzt weiterhin `CallbackAPIVersion.VERSION2`; sein 2.2.0-Release entfernt Python 3.7/3.8 und ändert bei einigen ungültigen API-Argumenten Ausnahmetypen ([Upstream-Release](https://github.com/eclipse-paho/paho.mqtt.python/releases/tag/v2.2.0)).
Die Bridge übergibt die unterstützte VERSION2-Enumeration und verwendet keine der betroffenen fehlerhaften Aufrufvarianten.

## Lokale Tests und Containerprüfung

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q eltako2mqtt.py bridge_base.py state_feedback.py tests
bash -n run.sh
docker build --build-arg BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.18 -t eltako2mqtt:local .
docker run --rm --entrypoint python3 eltako2mqtt:local \
  -c 'from eltako2mqtt import EltakoMiniSafe2Bridge; print(EltakoMiniSafe2Bridge.__name__)'
```

Die CI prüft Python 3.11/3.14 und baut ein amd64-Image mit Import-Smoke-Test.
Mocks ersetzen keinen MiniSafe-/Home-Assistant-Hardwaretest; der [Testplan](TESTING_OPTIMISTIC_STATE.md) beschreibt die zusätzliche praktische Prüfung.
