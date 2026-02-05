# Release Notes

Dieses Dokument enthält detaillierte Release Notes für alle Versionen von Eltako2MQTT.

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
- **RSSI Sensor** - Signalstärken-Monitoring (`sensor`)
  - Einheit: dBm
  - Device Class: `signal_strength`

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
eltako/{SID}/rssi           # Signalstärke in dBm

# Befehle
eltako/{SID}/set            # "on", "off", "toggle"
```

#### FRWB Rauchmelder

```bash
# Status
eltako/{SID}/smoke          # "on" (Alarm) oder "off" (Normal)
eltako/{SID}/temperature    # Temperatur in °C
eltako/{SID}/rssi           # Signalstärke in dBm
```

### 🏠 Home Assistant Integration

**FSR14 Schalter:**
```yaml
switch:
  - platform: mqtt
    name: "Licht Wohnzimmer"
    state_topic: "eltako/20/state"
    command_topic: "eltako/20/set"
    # Automatisch via MQTT Discovery erstellt
```

**FRWB Rauchmelder:**
```yaml
binary_sensor:
  - platform: mqtt
    name: "Rauchmelder Küche Alarm"
    state_topic: "eltako/30/smoke"
    device_class: smoke
    
sensor:
  - platform: mqtt
    name: "Rauchmelder Küche Temperatur"
    state_topic: "eltako/30/temperature"
    unit_of_measurement: "°C"
    device_class: temperature
    # Automatisch via MQTT Discovery erstellt
```

### 📦 Installation & Update

#### Neue Installation

1. Navigieren Sie zu **Einstellungen** → **Add-ons** → **Add-on Store**
2. Klicken Sie auf die drei Punkte oben rechts → **Repositories**
3. Fügen Sie hinzu: `https://github.com/Olgrov/eltako2mqtt`
4. Suchen Sie "Eltako2MQTT" und klicken Sie **INSTALLIEREN**
5. Konfigurieren Sie das Add-on
6. Starten Sie das Add-on

#### Update von v1.1.0

1. Gehen Sie zu **Einstellungen** → **Add-ons** → **Eltako2MQTT**
2. Klicken Sie auf **UPDATE** (wenn verfügbar)
3. Starten Sie das Add-on neu
4. Ihre FSR14 und FRWB Geräte werden automatisch erkannt
5. Keine Konfigurationsänderungen erforderlich

**Hinweis:** Das Update ist vollständig rückwärtskompatibel. Ihre bestehenden Geräte funktionieren weiterhin ohne Änderungen.

### 🐛 Bekannte Einschränkungen

1. **FSR14M-2x Strommessung**: Aktuell nicht als separate Sensoren implementiert. Die Schaltfunktion funktioniert vollständig. Power-Monitoring kann in zukünftigen Versionen hinzugefügt werden.

2. **Geräte-Benennung**: Multi-Channel Geräte erscheinen mit ihren individuellen SIDs. Eine automatische Gruppierung oder bessere Benennung kann in zukünftigen Versionen implementiert werden.

### ✅ Kompatibilität

- ✅ Vollständig rückwärtskompatibel mit v1.1.0
- ✅ Keine Breaking Changes
- ✅ Bestehende Konfigurationen funktionieren ohne Änderungen
- ✅ Alle bisherigen Geräte (Blinds, Dimmers, Weather) weiterhin voll funktionsfähig
- ✅ Getestet mit Home Assistant 2025.x und 2026.x
- ✅ Unterstützt alle Architekturen: aarch64, amd64, armhf, armv7, i386

### 🔮 Ausblick auf zukünftige Versionen

Geplante Features für kommende Releases:

- **v1.3.0**: FSR14M-2x Power Measurement Sensoren
- **Zukünftig**: FHK14/F4HK14 Thermostat Support
- **Zukünftig**: FSDG14, FWZ14, F3Z14D Zähler Support
- **Zukünftig**: FRGBW14 RGBW Dimmer Support
- **Zukünftig**: Bessere Multi-Channel Geräte-Benennung

### 🙏 Danksagungen

Danke an [@M4XXXi](https://github.com/M4XXXi) für das Feature Request [#10](https://github.com/Olgrov/eltako2mqtt/issues/10) und das Testen mit echten FSR14 und FRWB Geräten.

### 📚 Weitere Informationen

- [CHANGELOG.md](CHANGELOG.md) - Technischer Changelog
- [README.md](README.md) - Hauptdokumentation
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

Für Details zu älteren Versionen (v1.0.5 und früher), siehe [CHANGELOG.md](CHANGELOG.md) oder Git History.

---

## Support & Feedback

Bei Fragen, Problemen oder Feature-Requests:

- **Issues**: https://github.com/Olgrov/eltako2mqtt/issues
- **Discussions**: https://github.com/Olgrov/eltako2mqtt/discussions
- **Pull Requests**: Contributions welcome!

---

*Dieses Dokument wird mit jedem Release aktualisiert.*
