# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [1.0.3-mqtt2.1.0-dev] - 2026-01-06 (TEST BRANCH)

### Experimental
- **TEST BRANCH**: paho-mqtt aktualisiert von 1.6.1 auf 2.1.0
- Refaktoriert für CallbackAPIVersion.VERSION1 (backward-compatible)
- Alle Callback-Funktionen mit `properties` Parameter erweitert
- Code-Dokumentation für MQTT 2.1.0 Kompatibilität hinzugefügt

### Breaking Changes
- Erfordert paho-mqtt 2.1.0 oder höher (nicht abwärtskompatibel zu 1.6.1)
- Client-Erstellung mit `callback_api_version` Parameter erforderlich

### Testing
- ⚠️ WARNUNG: Dies ist ein Testbranch - NUR für Testing verwenden!
- Gründliches Testing erforderlich bevor in Production

---

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