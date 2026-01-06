# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [1.0.2] - 2026-01-06

### Geändert
- Abhängigkeiten aktualisiert:
  - `PyYAML` auf 6.0.3 (Dependabot, merged PR #4).
  - `paho-mqtt` auf 2.1.0 (Dependabot, PR #5) — WICHTIG: paho-mqtt 2.x enthält breaking changes; siehe Hinweise unten.
  - `requests` auf 2.32.3 — gepinnte Version für reproduzierbare Builds.
- Dockerfile aktualisiert: Explizite Versionspinning aller Abhängigkeiten für Konsistenz mit `requirements.txt`.
- Wartungs- und Stabilitätsupdates an Container/Build-Setup.

### Sicherheit
- Aktualisierte Abhängigkeiten schließen bekannte Schwachstellen und verbessern Stabilität und Kompatibilität.

### Hinweise zur Migration (paho-mqtt 2.x)
- paho-mqtt 2.0+ führt Änderungen an der Callback-API ein. Wenn das Projekt paho-mqtt Client-Instanzen verwendet, muss die Client-Initialisierung sowie Callback-Signaturen überprüft und ggf. angepasst werden (z. B. Übergabe von `CallbackAPIVersion.VERSION1` beim Erstellen eines `Client`).
- Achten Sie auf Unterschiede in Rückgabewerten/Typen (z. B. `dup`/`retain` sind nun booleans) und auf Verwendung von `is` zum Vergleich numerischer Fehlercodes (verwenden Sie `==`).
- Vor dem Release: Tests/Integration mit einem MQTT-Broker ausführen.

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
