# Release Notes

Dieses Dokument enthält detaillierte Release Notes für alle Versionen von Eltako2MQTT.

## Version 1.4.0 - Aktuelle 64-Bit-Plattform und Repository-Wartung (2026-11-13)

v1.4.0 modernisiert die Laufzeit und unterstützt ausschließlich `amd64` und `aarch64`.
Das bisherige [Release v1.3.0](https://github.com/Olgrov/eltako2mqtt/releases/tag/v1.3.0) bleibt unverändert die letzte veröffentlichte Version für `armhf`, `armv7` und `i386`; die alten Release-Tags werden nicht verschoben und es wird keine weiter gepflegte 32-Bit-Linie eröffnet.

### Plattform und geprüfte Abhängigkeiten

| Bestandteil | Stand bei Release-Prüfung |
| --- | --- |
| Add-on-Architekturen | amd64, aarch64 |
| Offizielle Basis | `ghcr.io/home-assistant/base-python:3.15-alpine3.24`, Multi-Arch |
| Python | 3.15.2, neueste stabile Version; keine 3.16-Vorabversion |
| Alpine | Stabile 3.24-Linie, aktuelle Pakete durch `apk upgrade` beim Build |
| pip im Basisimage | 26.3 |
| aiohttp | 3.14.5, bereits neuestes stabiles direktes Release |
| paho-mqtt | 2.2.0, bereits neuestes stabiles direktes Release |
| PyYAML | 6.0.3, bereits neuestes stabiles direktes Release |

Der Stand wurde am 13. November 2026 anhand der [Python-Releases](https://www.python.org/downloads/), der [offiziellen Home-Assistant-Basisimages](https://github.com/home-assistant/docker-base) und von PyPI geprüft ([aiohttp](https://pypi.org/project/aiohttp/), [Paho](https://pypi.org/project/paho-mqtt/), [PyYAML](https://pypi.org/project/PyYAML/)).
Die drei direkten Pins waren bereits aktuell und werden nicht unnötig geändert; transitive Abhängigkeiten werden frisch aufgelöst und mit `pip check` geprüft.
Python/Pip kommen aus dem offiziellen Python-Basisimage, nicht mehr aus alten Alpine-Paketen; benötigte Source-Build-Werkzeuge werden anschließend entfernt.
Der Launcher validiert Pflichtfelder direkt aus der lokalen `options.json`, ohne dafür auf die inzwischen API-basierte Bashio-Konfigurationsabfrage zurückzugreifen.
Zusätzliche Supervisor-API-Berechtigungen werden nicht benötigt.

### Upgrade und 32-Bit-Migration

1. Vollständiges Backup erstellen und die Architektur des Home-Assistant-Systems prüfen.
2. Auf amd64/aarch64 das Add-on auf v1.4.0 aktualisieren beziehungsweise das neue Image bauen.
3. Startzeile `Eltako2MQTT 1.4.0; poll interval=30s; feedback timeout=120s` und Gerätefunktionen prüfen.
4. Auf einem 32-Bit-System v1.4.0 nicht erzwingen; zunächst das unveränderte v1.3.0-Image/Backup behalten und auf ein unterstütztes 64-Bit-System migrieren.

Slug, Standard-MQTT-Client-ID, Topics, Discovery-IDs und Konfigurationsoptionen bleiben erhalten.
Nach einer 64-Bit-Migration müssen Entitäten und Automatisierungen nicht gelöscht werden; Details und Legacy-Quellstand stehen in der [Installationsanleitung](INSTALLATION.md#32-bit-systeme-und-letzter-legacy-stand).
Die Aufbewahrung von v1.3.0 ist keine Zusage weiterer Sicherheitsupdates für dessen alte Plattform.

<a name="noch-nicht-veröffentlicht---repository-wartung"></a>

### Enthaltene Repository-Wartung

Die seit v1.3.0 vorbereitete Bereinigung ist nun Teil dieses Releases: ersetzte Altimplementierungen, ungenutzte Manifest-Zugriffe und der doppelte YAML-Installationsweg sind entfernt.
GitHub Actions sind aktuell und SHA-gepinnt; die experimentelle Historie ist im Haupt-Changelog zusammengeführt und historische RSSI-/Rauchmelder-Beispiele sind korrigiert.
Bisherige Dokumentations-URLs und alte Überschriftenanker bleiben erhalten; der Apache-2.0-Lizenztext ist vollständig enthalten.
Die zwischenzeitlich getrennte Basis-Migration ist mit v1.4.0 und der ausdrücklich beschlossenen 64-Bit-Beschränkung abgeschlossen.

### Validierung und Grenzen

- **Python:** Regressionen auf Python 3.14 und 3.15 sowie Abhängigkeitsprüfung.
- **Container:** Native Builds und Tests für amd64/aarch64, tatsächliche Laufzeit-/Alpine-Prüfung und Unittests im fertigen Image.
- **Standardstart:** S6/Bashio-Entrypoint, Konfigurationsübergabe, MQTT-Discovery, Polling, Rollladen-/Dimmer-/Schalterbefehle, Sensoren und Shutdown gegen lokale MiniSafe-/MQTT-Fakes.
- **Kompatibilität:** CI prüft den unveränderten v1.3.0-Tag und dessen fünf ursprüngliche Architekturen; für v1.4.0 werden nur zwei Architekturen gebaut.
- **Dokumentation:** Lokale Link-/Ankerprüfung; bisherige Dokumentations-URLs bleiben erhalten.
- **Grenze:** Kein neuer physischer MiniSafe-/Home-Assistant-Frontend-Test; der Smoke-Test pollt nur seine Fakes im Ein-Sekunden-Takt, echte Geräte weiterhin mit mindestens 30 Sekunden betreiben.

Vollständige Änderungen stehen im [Changelog zu v1.4.0](../CHANGELOG.md#140---2026-11-13).

## Version 1.3.0 - Produktive Zustandsrückmeldung und MQTT-Update (2026-11-13)

Die erprobte Zustandsrückmeldung aus dem Testbranch ist jetzt Bestandteil des produktiven Add-ons.
Die Veröffentlichung verbindet [Release-PR #24](https://github.com/Olgrov/eltako2mqtt/pull/24) mit dem `paho-mqtt`-Update aus [PR #25](https://github.com/Olgrov/eltako2mqtt/pull/25).

### Funktionen und Korrekturen

- **Produktiver Start:** `run.sh` → `eltako2mqtt.py` → `StateFeedbackBridge`; vollständige Module im Docker-Image, keine experimentelle Identität.
- **Rollläden:** Sofortige angenommene Bewegungsanzeige nach Befehlsannahme; echte gepollte Position bleibt unverändert. Alte oder gegenläufige Proben beenden den neuesten Befehl nicht vorzeitig.
- **Bestätigung:** Pending-Tracking je SID, Zielvergleich und Ersatzbefehle. Standardmäßig 120 Sekunden unabhängiger Feedback-Timeout, auch wenn erfolgreiche Polls ausbleiben.
- **Keine Zusatzlast:** Standard 30 Sekunden Polling, gemeinsame HTTP-Serialisierung, Mindestabstand zwischen GetStates-Starts und keine Abfrage pro Befehl.
- **Schalter/Dimmer:** Optimistische Home-Assistant-Bedienung und reale MQTT-Statuswerte; ungültige Dimmerhelligkeit setzt den letzten gültigen Wert nicht auf 0.
- **Paketierung:** Docker installiert aus `requirements.txt`. Version 1.3.0, Name/Slug und Standard-Client-ID sind konsistent produktiv.
- **Konfiguration:** Optionaler Timeout wird korrekt weitergereicht; Passwörter werden ohne Shell-/YAML-Interpolation übertragen.
- **Prüfung:** Feedback-Regressionen sowie produktive Startpfad-, Metadaten- und Konfigurationstests; CI für Python 3.11/3.14 und amd64-Container.
- **Discovery:** Jede Konfiguration wird einmal mit den endgültigen Feedback-Einstellungen publiziert, nicht zunächst mit alten Einstellungen überschrieben.
- **Dokumentation:** Sämtliche aktuellen Guides einschließlich MQTT-Skalen, tatsächlichen Topics, Upgrade und Testbranch-Migration überarbeitet.

### Abhängigkeiten und Kompatibilität

`paho-mqtt` steigt von 2.1.0 auf 2.2.0; `aiohttp==3.14.5` und `PyYAML==6.0.3` bleiben unverändert.
Die VERSION2-Callbacks bleiben erhalten.
Paho 2.2.0 unterstützt Python 3.7/3.8 nicht mehr; das Add-on nutzt Python 3.11 und ist davon nicht betroffen ([Upstream-Release](https://github.com/eclipse-paho/paho.mqtt.python/releases/tag/v2.2.0)).

### Upgrade und Migration

1. Backup und Konfiguration sichern, Add-on Store neu laden und 1.3.0 installieren/bauen.
2. Vorhandenen `poll_interval` prüfen: Standard ist 30 Sekunden, alte Werte unter 30 werden nicht automatisch überschrieben und sind nicht empfohlen.
3. Optional `eltako.command_feedback_timeout: 120` ergänzen; an längste Fahrt plus Rückmeldeverzögerung anpassen, Add-on-Bereich 30–900.
4. Test-Add-on stoppen und Autostart deaktivieren, bevor Produktion startet.
5. Logzeile `Eltako2MQTT 1.3.0; poll interval=30s; feedback timeout=120s` und Gerätefunktionen prüfen.

Produktiver Slug, Client-ID-Standard, Command-Topics und Discovery-IDs bleiben erhalten.
Entitäten und Automatisierungen müssen nicht gelöscht oder neu angelegt werden; Discovery wird erneut veröffentlicht.
Der Cover-Movement-Topic ist zusätzlich, und die Discovery nutzt ihn für die Bewegungsanzeige.
Der bisherige Rohpositions-Topic bleibt unverändert.

### Wichtige Semantik und Grenzen

- **Positionsskalen:** MQTT-Befehl/Home Assistant 0=geschlossen und 100=offen; MQTT-Rohstatus/MiniSafe 0=offen und 100=geschlossen. Keine zusätzliche Invertierung durch eigene Publisher.
- **Bewegung:** `opening`/`closing` sind Annahmen, keine gemessenen Motorzustände. Auch eine Positionsprobe nach Stop bestätigt keinen unabhängigen Motorstillstand.
- **Timeout:** Beendet Tracking und Annahme, nicht die reale Fahrt; kein automatischer Retry und keine künstliche Zielposition.
- **Polling:** Rückmeldung kann mehrere Polls verspätet eintreffen; keine garantierte Echtzeit-Latenz. Nicht zur Kompensation schneller pollen.
- **Verfügbarkeit:** Kein Availability-/LWT-Topic; retained Werte können nach einem Ausfall veraltet sein.
- **Umfang:** Keine FSR14M-Leistungsmessung, keine neuen Gerätetypen und kein Ersatz für zertifizierte Rauchalarmierung.
- **Validierung:** Automatisierte Tests/Container-Imports ersetzen keine erneute Prüfung mit dem eigenen MiniSafe und Home-Assistant-Frontend.

Details stehen in [Installation](INSTALLATION.md), [MQTT-Referenz](MQTT_COMMANDS.md), [API](API.md) und [Testplan](TESTING_OPTIMISTIC_STATE.md).
Die folgenden Abschnitte dokumentieren frühere Versionen und können frühere Polling-/Logging-Verträge beschreiben.

---

## Version 1.2.5 - aiohttp 3.14.5 Maintenance Update (2026-10-27)

### 🎯 Überblick

Version 1.2.5 ist ein Wartungsrelease. Es aktualisiert `aiohttp` von **3.14.3** auf **3.14.5** und synchronisiert die Add-on-Version in `config.yaml`, dem Docker-Image-Label und der Dokumentation.

### 🔧 Änderungen

- `aiohttp` wurde in `requirements.txt` und `Dockerfile` auf **3.14.5** aktualisiert.
- Die Add-on-Version in `config.yaml` und `io.hass.version` wurde auf **1.2.5** angehoben.
- README, Installationsanleitung, Changelog und Release Notes wurden für v1.2.5 aktualisiert.

### ✅ Auswirkungen

- Keine Änderungen an Gerätelogik, MQTT-Topics oder Home Assistant Discovery.
- Keine Konfigurationsmigration erforderlich.
- Vollständig rückwärtskompatibel zu v1.2.4 und früheren v1.2.x-Versionen.

### 📦 Upgrade

Das Add-on kann direkt über den Home Assistant Add-on Store aktualisiert werden. Bestehende Konfigurationen und Automatisierungen bleiben unverändert.

---

<a name="version-124---aiohttp-3143-security--compatibility-update-2026-07-31"></a>

## Version 1.2.4 - aiohttp 3.14.3 Security & Compatibility Update (2026-09-03)

### 🎯 Überblick

Version 1.2.4 ist ein reines Wartungs- und Sicherheitsrelease, das die verwendete `aiohttp`-Version auf **3.14.3** anhebt und sämtliche Build-Umgebungen konsistent aktualisiert.
Die Datumsangabe folgt der Veröffentlichung des [GitHub-Releases v1.2.4](https://github.com/Olgrov/eltako2mqtt/releases/tag/v1.2.4); das Abhängigkeitsupdate wurde bereits am 31. Juli übernommen.

---

## Version 1.2.3 - aiohttp 3.14.2 Update (2026-07-25)

Version 1.2.3 aktualisiert `aiohttp` von 3.14.1 auf 3.14.2 und gleicht `requirements.txt` und Dockerfile ab.
Das [GitHub-Release v1.2.3](https://github.com/Olgrov/eltako2mqtt/releases/tag/v1.2.3) wurde am 25. Juli 2026 veröffentlicht; die Geräte- und MQTT-Schnittstellen bleiben unverändert.

---

## Version 1.2.2 - aiohttp 3.14.1 Security & Compatibility Update (2026-06-15)

### 🎯 Überblick

Version 1.2.2 ist ein reines Wartungs- und Sicherheitsrelease, das die verwendete `aiohttp`-Version auf **3.14.1** anhebt und sämtliche Build-Umgebungen (Dockerfiles und `requirements.txt`) konsistent aktualisiert.

### 🔐 Änderungen

- Aktualisiert `aiohttp` von `3.13.5` auf `3.14.1` in allen relevanten Komponenten:
  - `eltako2mqtt/requirements.txt`
  - `eltako2mqtt/Dockerfile`
  - root `Dockerfile`
- Stellt sicher, dass zur Laufzeit und zur Build-Zeit dieselbe HTTP-Bibliothek verwendet wird.
- Hebt die Add-on-Version auf **1.2.2** in `config.yaml` und im Docker-Label (`io.hass.version`) an.

### ✅ Auswirkungen

- Keine funktionalen Änderungen an unterstützten Geräten (FSR14, FRWB, Blinds, Dimmer etc.).
- Keine Änderungen an MQTT-Topics oder Home Assistant Discovery.
- Vollständig rückwärtskompatibel zu v1.2.1 und v1.2.0.
- Empfohlenes Update, um von den aktuellen Bugfixes und Security-Patches der `aiohttp`-Bibliothek zu profitieren.

---

## Version 1.2.1 - Dependency & Security Update (2026-04-02)

### 🎯 Überblick

Version 1.2.1 ist ein kleines Wartungs- und Sicherheitsrelease ohne funktionale Änderungen an den unterstützten Geräten.
Es synchronisiert die verwendete `aiohttp`-Version im Docker-Image mit `requirements.txt` und aktualisiert die interne Add-on-Versionsführung.

### 🔐 Änderungen

- Aktualisiert `aiohttp` von `3.13.3` auf `3.13.5` im Docker-Image.
- Stellt sicher, dass `requirements.txt` und Dockerfile dieselbe `aiohttp`-Version verwenden.
- Hebt die Add-on-Version auf **1.2.1** in `config.yaml` und im Docker-Label an.

### ✅ Auswirkungen

- Keine neuen Features, kein Breaking Change.
- Bestehende Konfigurationen funktionieren unverändert.
- Empfohlenes Update, um auf den aktuellsten Patch-Stand der HTTP-Bibliothek zu kommen.

---

## Version 1.2.0 - FSR14 Switch Actuators & FRWB Smoke Detectors (2026-02-05)

### 🎯 Überblick

Version 1.2.0 erweitert die Geräteunterstützung um die FSR14 Schaltaktoren-Familie und FRWB Rauchmelder. Diese Version wurde entwickelt, um die am häufigsten angefragten Eltako-Geräte zu unterstützen und gleichzeitig die Code-Qualität durch eine neue Helper-Funktion zu verbessern.

### ✨ Neue Features

#### FSR14 Schaltaktoren Familie

Vollständige Unterstützung für alle FSR14 Varianten:

- **FSR14** (1-4 Kanäle) - Standard Schaltaktor
- **FSR14M-2x** (mit Strommessung)* - Energiemessung möglich
- **FSR14SSR** (Solid State Relay) - Elektronisches Schaltrelais
- **F4SR14-LED** (4-fach für LED) - Speziell für LED-Steuerung
- **FAE14LPR, FAE14SSR** - Weitere Schaltaktoren

*Hinweis: Strommessungs-Sensoren können in zukünftigen Versionen als zusätzliche Entities hinzugefügt werden.*

**Funktionen:**
- Standard Schaltbefehle: `on`, `off`, `toggle`
- Automatische Home Assistant Discovery als `switch` Entity
- Echtzeit-Statusaktualisierung via MQTT
- RSSI Signalstärken-Monitoring

**Mehrkanalige Geräte:**
- FSR14-4x und ähnliche Multi-Channel Geräte werden automatisch unterstützt
- MiniSafe2 meldet jeden Kanal als separates Gerät mit aufeinanderfolgenden SIDs
- Beispiel: FSR14-4x auf SID 20 → Kanäle erscheinen als SID 20, 21, 22, 23
- Jeder Kanal wird als eigene Switch-Entity in Home Assistant erkannt
- Keine spezielle Konfiguration erforderlich

#### FRWB Rauchmelder

Komplette Integration für FRWB Rauchmelder:

- **Binary Sensor** - Rauchalarm-Detektion (`binary_sensor`)
  - State: `on` = Alarm aktiv
  - State: `off` = Normal
- **Temperatursensor** - Eingebauter Temperatursensor (`sensor`)
  - Einheit: °C
  - Device Class: `temperature`
- **RSSI MQTT-Topic** - Signalstärken-Monitoring über `rssiPercentage`
  - Einheit: Prozent, nicht dBm
  - Kein eigener automatisch entdeckter RSSI-Sensor

**Funktionen:**
- Automatische Home Assistant Discovery
- Echtzeit-Alarm-Updates
- Raumtemperatur-Überwachung
- Funkverbindungs-Monitoring

### 🔧 Technische Verbesserungen

#### Neue `is_switch_device()` Helper-Funktion

Eine zentrale Funktion zur Erkennung von Schaltgeräten:

```python
def is_switch_device(self, device_type: str) -> bool:
    """Check if device is a switch-type actuator"""
    device_type_lower = device_type.lower()
    return any(keyword in device_type_lower for keyword in [
        'switch',
        'fsr14',       # All FSR14 variants
        'f4sr14',      # 4-channel switch
        'fae14'        # FAE14 switch actuators
    ])
```

**Vorteile:**
- Sauberer, wartbarer Code
- Single Source of Truth für Geräte-Typ-Prüfung
- Einfache Erweiterung für neue Switch-Varianten
- Reduziert Code-Duplikation

**Verwendung in:**
- `build_command_url()` - Befehlsverarbeitung
- `update_device_state_immediate()` - Sofortige State-Updates
- `publish_device_state()` - MQTT State Publishing
- `publish_discovery()` - Home Assistant Discovery
- `_log_device_feedback()` - Debug Logging

### 📋 MQTT Topics

#### FSR14 Schalter

```bash
# Status
eltako/{SID}/state          # "on" oder "off"
eltako/{SID}/rssi           # Signalstärke in Prozent

# Befehle
eltako/{SID}/set            # "on", "off", "toggle"
```

#### FRWB Rauchmelder

```bash
# Status
eltako/{SID}/smoke          # "true" (Alarm) oder "false" (Normal)
eltako/{SID}/temperature    # Temperatur in °C
eltako/{SID}/rssi           # Signalstärke in Prozent
```

### 🏠 Home Assistant Integration

**FSR14 Schalter:**

Die folgenden manuellen MQTT-Beispiele sind an die aktuelle Konfigurationsstruktur angepasst.
Normalerweise werden die Entitäten automatisch über Discovery erstellt und benötigen keine manuelle YAML-Konfiguration.

```yaml
mqtt:
  switch:
    - name: "Licht Wohnzimmer"
      state_topic: "eltako/20/state"
      command_topic: "eltako/20/set"
      payload_on: "on"
      payload_off: "off"
```

**FRWB Rauchmelder:**
```yaml
mqtt:
  binary_sensor:
    - name: "Rauchmelder Küche Alarm"
      state_topic: "eltako/30/smoke"
      device_class: smoke
      payload_on: "true"
      payload_off: "false"
  sensor:
    - name: "Rauchmelder Küche Temperatur"
      state_topic: "eltako/30/temperature"
      unit_of_measurement: "°C"
      device_class: temperature
```

### 📦 Installation & Update

#### Neue Installation

1. Navigieren Sie zu **Einstellungen** → **Add-ons** → **Add-on Store**
2. Klicken Sie auf die drei Punkte oben rechts → **Repositories**
3. Fügen Sie hinzu: `https://github.com/Olgrov/eltako2mqtt`
4. Suchen Sie "Eltako2MQTT" und klicken Sie **INSTALLIEREN**
5. Konfigurieren Sie das Add-on
6. Starten Sie das Add-on

#### Update von v1.1.0 oder v1.2.x

1. Gehen Sie zu **Einstellungen** → **Add-ons** → **Eltako2MQTT**
2. Klicken Sie auf **UPDATE** (wenn verfügbar)
3. Starten Sie das Add-on neu
4. Ihre bestehenden Geräte werden automatisch erkannt
5. Keine Konfigurationsänderungen erforderlich

**Hinweis:** Das Update auf v1.2.2 ist vollständig rückwärtskompatibel. Ihre bestehenden Geräte und Automatisierungen funktionieren weiterhin ohne Änderungen.

### 🐛 Bekannte Einschränkungen

1. **FSR14M-2x Strommessung**: Aktuell nicht als separate Sensoren implementiert. Die Schaltfunktion funktioniert vollständig. Power-Monitoring kann in zukünftigen Versionen hinzugefügt werden.

2. **Geräte-Benennung**: Multi-Channel Geräte erscheinen mit ihren individuellen SIDs. Eine automatische Gruppierung oder bessere Benennung kann in zukünftigen Versionen implementiert werden.

### ✅ Kompatibilität

- ✅ Vollständig rückwärtskompatibel mit v1.1.0, v1.2.0 und v1.2.1
- ✅ Keine Breaking Changes
- ✅ Bestehende Konfigurationen funktionieren ohne Änderungen
- ✅ Alle bisherigen Geräte (Blinds, Dimmer, Weather, FSR14, FRWB) weiterhin voll funktionsfähig
- ✅ Getestet mit Home Assistant 2025.x und 2026.x
- ✅ Unterstützt alle Architekturen: aarch64, amd64, armhf, armv7, i386

### 🔮 Ausblick auf zukünftige Versionen

Geplante Features für kommende Releases:

- **Zukünftig, ohne Versionszusage**: FSR14M-2x Power Measurement Sensoren (nicht in v1.3.0 enthalten)
- **Zukünftig**: FHK14/F4HK14 Thermostat Support
- **Zukünftig**: FSDG14, FWZ14, F3Z14D Zähler Support
- **Zukünftig**: FRGBW14 RGBW Dimmer Support
- **Zukünftig**: Bessere Multi-Channel Geräte-Benennung

### 🙏 Danksagungen

Danke an [@M4XXXi](https://github.com/M4XXXi) für das Feature Request [#10](https://github.com/Olgrov/eltako2mqtt/issues/10) und das Testen mit echten FSR14 und FRWB Geräten.

### 📚 Weitere Informationen

- [CHANGELOG.md](../CHANGELOG.md) - Technischer Changelog
- [README.md](../README.md) - Hauptdokumentation
- [INSTALLATION.md](INSTALLATION.md) - Installationsanleitung
- [MQTT_COMMANDS.md](MQTT_COMMANDS.md) - MQTT Befehls-Referenz
- [API.md](API.md) - API Dokumentation für Entwickler

---

## Version 1.1.0 - Position Control & Enhanced Logging (2026-01-09)

### 🎯 Überblick

Version 1.1.0 brachte bedeutende Verbesserungen für Jalousien-Steuerung, defensives Brightness-Handling für Dimmer und intelligentes Logging. Diese Version fokussierte sich auf Zuverlässigkeit und Benutzerfreundlichkeit.

### ✨ Hauptfeatures

#### Position-basierte Jalousiensteuerung

- **0-100% Positionssteuerung** statt nur Open/Close/Stop
- Automatische Position-Invertierung für Eltako-Kompatibilität
- Befehle: `moveTo0` (offen) bis `moveTo100` (geschlossen)
- Korrekte Positions-Anzeige in Home Assistant UI

#### Defensives Brightness Handling

- Robuste Validierung in `eltako_level_to_mqtt_brightness()`
- Behandelt `None`, String-Inputs und Over-Limit Werte
- Graceful Fallback zu 0 bei ungültigen Eingaben
- Verhindert Dimmer-Crashes durch Bad Data

#### Intelligentes Logging

- **Connection-aware Logging**: Nur bei MQTT-Verbindung
- **Geräte-spezifisches Logging**: Nur kürzlich gesteuerte Geräte
- **Dynamic Command Timeout**: `poll_interval + 60 Sekunden`
- Reduzierter Log-Noise bei DEBUG Level

### 🔧 Technische Änderungen

- **Default poll_interval**: Reduziert von 15 auf 5 Sekunden
- Neue `mqtt_connected` Flag für Connection-Tracking
- Neue `_recently_commanded_device` für Targeted Logging
- Neue `_is_recently_commanded()` Methode
- Neue `_log_device_feedback()` Methode
- Lowercase Blind Commands: `open`, `close`, `stop`

### 📦 Kompatibilität

- ✅ Vollständig rückwärtskompatibel
- ✅ Keine Breaking Changes
- ✅ Bestehende Configs funktionieren ohne Änderungen

---

## Ältere Versionen

Für Details zu älteren Versionen (v1.0.5 und früher), siehe [CHANGELOG.md](../CHANGELOG.md) oder Git History.

---

## Support & Feedback

Bei Fragen, Problemen oder Feature-Requests:

- **Issues**: https://github.com/Olgrov/eltako2mqtt/issues
- **Discussions**: https://github.com/Olgrov/eltako2mqtt/discussions
- **Pull Requests**: Contributions welcome!

---

Dieses Dokument wird mit jedem Release aktualisiert.
