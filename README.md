# [Eltako2MQTT - Eltako MiniSafe2 Home Assistant Add-on](https://github.com/Olgrov/eltako2mqtt)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

[Eltako MiniSafe2 to MQTT Bridge für Home Assistant](https://github.com/Olgrov/eltako2mqtt)

## About

Dieses Add-on stellt eine Brücke zwischen dem Eltako MiniSafe2 System und MQTT her, wodurch alle konfigurierten EnOcean-Geräte automatisch in Home Assistant verfügbar werden.

**Unterstützte Gerätetypen:**
- Jalousien/Rollläden (`eltako_blind`, `eltako_tf_blind`) - mit **Positionssteuerung** (0-100%)
- Schalter (`eltako_switch`, `eltako_tf_switch`) - on/off/toggle
- **FSR14 Schaltaktoren** - FSR14, FSR14M-2x, FSR14SSR, F4SR14-LED, FAE14 ✨ **NEU in v1.2.0**
- Dimmer (`eltako_dimmer`, `eltako_tf_dimmer`) - mit **robustem Helligkeitshandling**
- Wetterstationen (`eltako_weather`) - Temperatur, Wind, Regen, Helligkeit
- **Rauchmelder (FRWB)** - Rauchalarm + Temperatur ✨ **NEU in v1.2.0**

## 🆕 Was ist neu in v1.2.0?

### ✨ Neue Geräte
- **FSR14 Schaltaktoren Familie** - Vollständige Unterstützung
  - FSR14 (1-4 Kanäle)
  - FSR14M-2x (mit Strommessung)*
  - FSR14SSR (Solid State Relais)
  - F4SR14-LED (4-fach für LED-Steuerung)
  - FAE14LPR, FAE14SSR
- **FRWB Rauchmelder** - Komplette Integration
  - Binary Sensor für Rauchalarm
  - Temperatursensor
  - RSSI Signalstärke

*Strommessung kann in zukünftigen Versionen als zusätzlicher Sensor hinzugefügt werden

### 🚀 Verbesserungen
- Sauberer, wartbarer Code durch neue `is_switch_device()` Helper-Funktion
- Mehrkanalige Geräte (FSR14-4x) automatisch unterstützt
- Jeder Kanal erscheint als eigene Switch-Entity in Home Assistant
- Nutzt bewährte Patterns von bestehenden Gerätetypen

### Was ist neu in v1.1.0?

- **Position-basierte Jalousiensteuerung** - Kontrolle mit 0-100% Position
- **Defensives Helligkeitshandling** - Robuste Validierung für Dimmer
- **Intelligentes Logging** - Nur gesteuerte Geräte bei MQTT-Verbindung geloggt
- **Optimiertes Polling** - Standard 5 Sekunden statt 15 (schnellere Updates)
- **Konfigurierbare Log-Level** - DEBUG, INFO, WARNING, ERROR

## Installation

1. Navigieren Sie zu **Einstellungen** → **Add-ons** → **Add-on Store**
2. Klicken Sie auf die drei Punkte oben rechts → **Repositories**
3. Fügen Sie diese Repository-URL hinzu: https://github.com/Olgrov/eltako2mqtt
4. Aktualisieren Sie die Seite
5. Suchen Sie nach "Eltako2MQTT" und klicken Sie auf **INSTALLIEREN**

## Konfiguration

```yaml
eltako:
  host: "192.168.1.100"          # IP-Adresse des Eltako MiniSafe2
  password: "your_password"      # Passwort für das MiniSafe2
  poll_interval: 5               # Abfrageintervall in Sekunden (Standard: 5)

mqtt:
  host: "core-mosquitto"         # MQTT Broker Host
  port: 1883                     # MQTT Port
  username: ""                   # MQTT Benutzername (optional)
  password: ""                   # MQTT Passwort (optional)
  client_id: "eltako2mqtt"       # MQTT Client ID

logging:
  level: "INFO"                  # Log-Level: DEBUG, INFO, WARNING, ERROR
```

### Konfigurationsoptionen

#### Option: `eltako.host` (erforderlich)
Die IP-Adresse Ihres Eltako MiniSafe2 Systems.

#### Option: `eltako.password` (erforderlich)
Das Passwort für den Zugriff auf das MiniSafe2 System.

#### Option: `eltako.poll_interval` (optional)
Intervall in Sekunden für die Abfrage der Gerätezustände (Standard: **5** Sekunden).
- Schneller (3-5): Responsiver, etwas mehr Netzwerk-Traffic
- Standard (5): Ausgewogene Balance (empfohlen)
- Langsamer (15+): Weniger Traffic, langsamere Updates

#### Option: `mqtt.host` (erforderlich)
Der Hostname oder die IP-Adresse des MQTT-Brokers (Standard: "core-mosquitto").

#### Option: `mqtt.port` (optional)
Der Port des MQTT-Brokers (Standard: 1883).

#### Option: `mqtt.username` & `mqtt.password` (optional)
MQTT-Zugangsdaten falls erforderlich.

#### Option: `logging.level` (optional)
Log-Level zur Steuerung der Ausgabe-Verbosität:
- `DEBUG` - Alles, inklusive Hardware-Feedback (nur für gesteuerte Geräte bei MQTT-Verbindung)
- `INFO` - Standard, wichtige Informationen
- `WARNING` - Nur Warnungen
- `ERROR` - Nur Fehler

## Verwendung

Nach der Installation und Konfiguration:

1. **Automatische Geräteerkennung**: Das Add-on erkennt automatisch alle konfigurierten Geräte
2. **Home Assistant Integration**: Alle Geräte werden automatisch in Home Assistant über MQTT Discovery verfügbar
3. **Echtzeitsteuerung**: Befehle werden sofort an das MiniSafe2 System weitergeleitet

### MQTT Topics

- **Status**: `eltako/{SID}/state` - Aktueller Gerätestatus
- **Befehle**: `eltako/{SID}/set` - Befehle senden
- **RSSI**: `eltako/{SID}/rssi` - Signalstärke
- **Helligkeit (Dimmer)**: `eltako/{SID}/brightness` - 0-255
- **Jalousienposition**: `eltako/{SID}/pos` - 0-100%
- **Rauchmelder**: `eltako/{SID}/smoke` - binary sensor (on/off)
- **Temperatur (Rauchmelder)**: `eltako/{SID}/temperature` - °C

### Beispiel-Befehle

**FSR14 Schalter (neu in v1.2.0):**
```bash
# Einschalten
mosquitto_pub -t "eltako/20/set" -m "on"
# Ausschalten
mosquitto_pub -t "eltako/20/set" -m "off"
# Umschalten
mosquitto_pub -t "eltako/20/set" -m "toggle"
```

**Jalousien:**
```bash
# Öffnen (Position 0)
mosquitto_pub -t "eltako/01/set" -m "open"
# Schließen (Position 100)
mosquitto_pub -t "eltako/01/set" -m "close"
# Zu Position 50% fahren
mosquitto_pub -t "eltako/01/set" -m "50"
# Stoppen
mosquitto_pub -t "eltako/01/set" -m "stop"
```

**Schalter:**
```bash
# Einschalten
mosquitto_pub -t "eltako/11/set" -m "on"
# Ausschalten
mosquitto_pub -t "eltako/11/set" -m "off"
# Umschalten
mosquitto_pub -t "eltako/11/set" -m "toggle"
```

**Dimmer:**
```bash
# Einschalten
mosquitto_pub -t "eltako/13/set" -m "on"
# Ausschalten
mosquitto_pub -t "eltako/13/set" -m "off"
# Dimmen auf 50%
mosquitto_pub -t "eltako/13/set" -m "50"
# Auf Helligkeit 200 (0-255 Skala)
mosquitto_pub -t "eltako/13/set" -m "200"
```

## Home Assistant Integration

Alle Geräte werden automatisch über MQTT Discovery erkannt:

- **Jalousien** → Home Assistant `cover` Entity mit Position
- **Schalter** → Home Assistant `switch` Entity
- **FSR14 Aktoren** → Home Assistant `switch` Entity (je Kanal)
- **Dimmer** → Home Assistant `light` Entity mit Helligkeit
- **Wetterstation** → Mehrere `sensor` Entities (Temp, Wind, Regen, Helligkeit)
- **Rauchmelder** → `binary_sensor` (Rauch) + `sensor` (Temperatur, RSSI)

Keine manuelle Konfiguration in Home Assistant erforderlich!

## Troubleshooting

### Add-on zeigt "Connection refused"
- Prüfen Sie die IP-Adresse und das Passwort des MiniSafe2
- Stellen Sie sicher, dass MiniSafe2 im gleichen Netzwerk erreichbar ist
- Testen Sie die Verbindung: `ping 192.168.1.100` (Ihre IP)

### Geräte erscheinen nicht in Home Assistant
1. Gehen Sie zu **Einstellungen** → **Add-ons** → **Eltako2MQTT** → **Log**
2. Setzen Sie Log-Level auf "DEBUG"
3. Prüfen Sie, ob Geräte erkannt werden:
   - Suchen Sie nach "Found device"
   - Suchen Sie nach "Published discovery"
4. Falls Fehler angezeigt: Überprüfen Sie MQTT Broker Verbindung

### FSR14 oder Rauchmelder werden nicht erkannt
- Prüfen Sie im MiniSafe2 Web-Interface, ob die Geräte dort sichtbar sind
- Achten Sie auf die korrekte Gerätebezeichnung (z.B. "FSR14", "FRWB")
- Setzen Sie Log-Level auf DEBUG und suchen Sie nach Geräteerkennung
- Bei Mehrkanalgeräten: Jeder Kanal hat eine eigene SID und erscheint separat

### Zu viel Log-Output
- Setzen Sie `logging.level` auf "INFO" oder "WARNING"
- Bei v1.1.0+: Logging ist intelligent gefiltert (nur gesteuerte Geräte bei MQTT-Verbindung)

### Home Assistant erkennt Geräte nicht
- Stellen Sie sicher, dass MQTT Integration in Home Assistant aktiv ist
- Prüfen Sie MQTT Discovery ist aktiviert: **Einstellungen** → **Integrationen** → **MQTT**
- Starten Sie das Add-on neu

## Support

Bei Problemen prüfen Sie die Add-on Logs:
1. Gehen Sie zu **Einstellungen** → **Add-ons** → **Eltako2MQTT**
2. Klicken Sie auf den **Log** Tab
3. Setzen Sie den Log-Level auf "DEBUG" für detaillierte Informationen

Issues melden: https://github.com/Olgrov/eltako2mqtt/issues

## Besondere Hinweise

### Helligkeitssensoren (Illumination)
Die Sensorwerte `illumination_east`, `illumination_south` und `illumination_west` werden intern mit 1000 multipliziert, damit sie als Lux (lx) korrekt in Home Assistant angezeigt werden.
Alle vier Helligkeitssensoren (`illumination`, `illumination_east`, `illumination_south`, `illumination_west`) werden zudem als ganze Zahlen ohne Nachkommastellen übertragen.

### Jalousiensteuerung
- Positionen werden automatisch invertiert für Eltako-Kompatibilität
- Position 0 = offen, Position 100 = geschlossen
- Die UI in Home Assistant zeigt korrekte Positionen

### Dimmer-Helligkeitssteuerung
- Robuste Validierung verhindert Crashes durch ungültige Werte
- Unterstützt 0-100% Skala UND 0-255 Brightness Skala
- Automatische Konvertierung in Home Assistant

### Mehrkanalige FSR14 Geräte
- MiniSafe2 meldet jeden Kanal als separates Gerät mit aufeinanderfolgenden SIDs
- Beispiel: FSR14-4x mit SID 20 → Kanäle erscheinen als SID 20, 21, 22, 23
- Jeder Kanal wird als eigene Switch-Entity in Home Assistant erkannt
- Keine spezielle Konfiguration erforderlich

### Rauchmelder (FRWB)
- Binary Sensor zeigt Rauchalarm-Status (on = Alarm, off = Normal)
- Temperatursensor zeigt aktuelle Raumtemperatur
- RSSI zeigt Signalstärke zur Überwachung der Funkverbindung

## Changelog & Releases

Alle Versionshinweise und neuen Features finden Sie in:
- [CHANGELOG.md](CHANGELOG.md) - Detaillierter technischer Changelog
- [Releases](https://github.com/Olgrov/eltako2mqtt/releases) - Release Notes mit Upgrade-Hinweisen

## Dependencies

- `paho-mqtt` 2.1.0 - Modern MQTT Client mit VERSION2 API
- `aiohttp` 3.13.3+ - Async HTTP Client
- `PyYAML` 6.0.3+ - YAML Config Parser

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
