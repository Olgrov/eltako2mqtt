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
- Jalousien/Rollläden (`eltako_blind`, `eltako_tf_blind`)
- Schalter (`eltako_switch`, `eltako_tf_switch`)
- Dimmer (`eltako_dimmer`, `eltako_tf_dimmer`)
- Wetterstationen (`eltako_weather`)

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
  poll_interval: 30              # Abfrageintervall in Sekunden (1-300)

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
Intervall in Sekunden für die Abfrage der Gerätezustände (Standard: 30).

#### Option: `mqtt.host` (erforderlich)
Der Hostname oder die IP-Adresse des MQTT-Brokers (Standard: "core-mosquitto").

#### Option: `mqtt.port` (optional)
Der Port des MQTT-Brokers (Standard: 1883).

#### Option: `mqtt.username` & `mqtt.password` (optional)
MQTT-Zugangsdaten falls erforderlich.

## Verwendung

Nach der Installation und Konfiguration:

1. **Automatische Geräteerkennung**: Das Add-on erkennt automatisch alle konfigurierten Geräte
2. **Home Assistant Integration**: Alle Geräte werden automatisch in Home Assistant über MQTT Discovery verfügbar
3. **Echtzeitsteuerung**: Befehle werden sofort an das MiniSafe2 System weitergeleitet

### MQTT Topics

- **Status**: `eltako/{SID}/state` - Aktueller Gerätestatus
- **Befehle**: `eltako/{SID}/set` - Befehle senden
- **RSSI**: `eltako/{SID}/rssi` - Signalstärke

### Beispiel-Befehle

**Jalousien:**
```bash
# Öffnen
mosquitto_pub -t "eltako/01/set" -m "OPEN"
# Schließen
mosquitto_pub -t "eltako/01/set" -m "CLOSE"
# Stoppen
mosquitto_pub -t "eltako/01/set" -m "STOP"
```

**Schalter:**
```bash
# Einschalten
mosquitto_pub -t "eltako/11/set" -m "ON"
# Ausschalten
mosquitto_pub -t "eltako/11/set" -m "OFF"
```

**Dimmer:**
```bash
# Einschalten
mosquitto_pub -t "eltako/13/set" -m "ON"
# Dimmen auf 50%
mosquitto_pub -t "eltako/13/set" -m "50"
```

## Support

Bei Problemen prüfen Sie die Add-on Logs:
1. Gehen Sie zu **Einstellungen** → **Add-ons** → **Eltako2MQTT**
2. Klicken Sie auf den **Log** Tab
3. Setzen Sie den Log-Level auf "DEBUG" für detaillierte Informationen

## Besondere Hinweise

**Helligkeitssensoren (Illumination):**  
Die Sensorwerte `illumination_east`, `illumination_south` und `illumination_west` werden intern mit 1000 multipliziert, damit sie als Lux (lx) korrekt in Home Assistant angezeigt werden.
Alle vier Helligkeitssensoren (`illumination`, `illumination_east`, `illumination_south`, `illumination_west`) werden zudem als ganze Zahlen ohne Nachkommastellen übertragen.

## Changelog & Releases

Alle Versionshinweise finden Sie in der [CHANGELOG.md](CHANGELOG.md).

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
