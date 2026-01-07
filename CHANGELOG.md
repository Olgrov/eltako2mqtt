# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [1.0.4] - 2026-01-07

### Geändert
- **MQTT API**: Upgrade auf `CallbackAPIVersion.VERSION2` für paho-mqtt 2.1.0
- **Callback-Funktionen**: Alle auf VERSION2 API aktualisiert für moderne Best Practices
  - `on_mqtt_connect()`: VERSION2 Signatur mit `ConnectFlags` und `ReasonCode`
  - `on_mqtt_disconnect()`: Vereinfachte Fehlerbehandlung mit `DisconnectFlags`
- **Logging**: Verbesserte Debug-Meldungen für VERSION2 API

### ✨ Verbesserungen
- Modernere paho-mqtt 2.1.0 Best Practices
- Bessere Typsicherheit durch neue Callback-Signaturen
- Konsistente Error-Handling mit `ReasonCode`
- Zukunftssicherer Code

### ✅ Getestet
- Vollständig mit 33+ Eltako Geräten getestet
- Alle Gerätetypen funktionieren: Jalousien, Schalter, Dimmer, Wetterstation
- MQTT Discovery funktioniert perfekt
- Alle Gerätezustände synchronisieren sich ordnungsgemäß
- Keine funktionalen Rückschritte

### 📝 Notizen
- Keine Breaking Changes für Nutzer
- Reine API-Modernisierung, keine neuen Funktionen
- Drop-in Replacement für v1.0.3

---

## [1.0.3] - 2026-01-07

### Geändert
- **Abhängigkeiten**: `paho-mqtt` von 1.6.1 auf 2.1.0 aktualisiert
- **Callback API**: Auf `CallbackAPIVersion.VERSION1` aktualisiert für paho-mqtt 2.1.0 Kompatibilität
- **on_mqtt_disconnect()**: Callback-Signatur korrigiert zur Unterstützung neuer paho-mqtt 2.1.0 Konventionen

### Getestet
- ✅ Vollständig mit verschiedenen Geräten getestet (Dimmer, Schalter, Jalousien, Wetterstation)
- ✅ MQTT Discovery funktioniert korrekt
- ✅ Alle Gerätezustände synchronisieren sich ordnungsgemäß
- ✅ Keine funktionalen Rückschritte

### Sicherheit
- `paho-mqtt` 2.1.0 beinhaltet Sicherheitsupdates und Verbesserungen gegenüber 1.6.1

### Hinweise
- Verwendet deprecated `CallbackAPIVersion.VERSION1`
- Zukünftiges Release wird auf `CallbackAPIVersion.VERSION2` aktualisieren
- Keine Breaking Changes für Nutzer, die von v1.0.2 upgraden

## [1.0.2] - 2026-01-06

### Geändert
- Dependencies aktualisiert: `PyYAML` von 6.0.1 auf 6.0.3 für neueste Stabilitätsverbesserungen.
- Dockerfile synchronisiert mit requirements.txt für konsistente Versionierung.

### Sicherheit
- PyYAML Update für neueste Parser-Verbesserungen und Stabilitäts-Patches.

## [1.0.1] - 2026-01-06

### Geändert
- Abhängigkeiten aktualisiert: `aiohttp` auf 3.13.3 (Dependabot).
- Kleines Wartungs- und Stabilitätsupdate; keine funktionalen Änderungen.
- Merge von Pull Request #3 (Dependabot) zur Aktualisierung von Sicherheits- und Wartungsabhängigkeiten.

### Sicherheit
- Aktualisierung von `aiohttp` schließt bekannte Probleme und verbessert die Stabilität der HTTP-Kommunikation.

## [1.0.0] - 2025-08-04

### Hinzugefügt
- Erstes Release des Eltako2MQTT Home Assistant Add-ons
- Vollständige Unterstützung für Eltako MiniSafe2 HTTP-API
- Automatische Geräteerkennung über `/command?XC_FNC=GetStates`
- Home Assistant MQTT Discovery Integration
- Unterstützung für folgende Gerätetypen:
  - Jalousien/Rollläden (`eltako_blind`, `eltako_tf_blind`)
  - Schalter (`eltako_switch`, `eltako_tf_switch`)
  - Dimmer (`eltako_dimmer`, `eltako_tf_dimmer`)
  - Wetterstationen (`eltako_weather`)
- Echtzeitsteuerung über MQTT-Befehle
- RSSI-Monitoring für alle Geräte
- Konfigurierbare Polling-Intervalle
- Mehrsprachige Unterstützung (Deutsch/Englisch)
- Umfassende Fehlerbehandlung und Logging
- Docker-Multi-Arch-Support (amd64, aarch64, armhf, armv7, i386)

### Geändert
- Adaptiert von der ursprünglichen mediola2mqtt Implementierung (https://github.com/andyboeh/mediola2mqtt)
- Angepasst für Eltako MiniSafe2 API-Struktur
- Verwendet HTTP GET statt POST für Befehle
- Parst `{XC_SUC}` Response-Format

### Sicherheit
- Sichere Passwort-Übertragung über URL-Encoding
