# Eltako2MQTT v1.3.0 Dokumentation

Die Dokumentation beschreibt den produktiven Stand mit Zustandsrückmeldung und `paho-mqtt` 2.2.0.
Historische Releaseabschnitte sind als Historie zu lesen, nicht als aktuelle Konfigurationsempfehlung.

## Einstieg und Betrieb

- **[README](../README.md):** Funktionen, Gerätetypen, Konfiguration und zentrale Grenzen.
- **[Installation und Upgrade](INSTALLATION.md):** Produktionsupdate, Wechsel vom Test-Add-on, Diagnose und Rückbau.
- **[MQTT-Referenz](MQTT_COMMANDS.md):** Command-Payloads, Status-Topics, Positionsskalen, Discovery und CLI-Beispiele.
- **[Release Notes](RELEASE_NOTES.md):** Änderungen in 1.3.0, Migrationshinweise und frühere Releases.
- **[Changelog](../CHANGELOG.md):** Technische Änderungshistorie.

## Entwicklung und Prüfung

- **[Architektur/API](API.md):** Produktiver Einstieg, Basisklasse, Feedback-Modul, MiniSafe-Protokoll und Tests.
- **[Feedback-Testplan](TESTING_OPTIMISTIC_STATE.md):** Automatisierte und praktische Regressionen für Produktion und Migration.
- **[Experimentelle Historie](CHANGELOG_EXPERIMENTAL.md):** Herkunft der Feedback-Implementierung; kein separater produktiver Startpfad.

## Wichtige Verträge

- **Version:** 1.3.0, Name/Slug `eltako2mqtt`, Standard-MQTT-Client-ID `eltako2mqtt`.
- **Polling:** Standard 30 Sekunden; kleinere bestehende Werte werden beibehalten, aber nicht empfohlen.
- **Feedback:** Optionaler unabhängiger Timeout, Standard 120 Sekunden; keine zusätzlichen Polls oder Retries.
- **Position:** MQTT-Befehl und Home Assistant 0=geschlossen/100=offen, MQTT-Rohstatus genau umgekehrt.
- **Betrieb:** Produktiv- und Test-Add-on nie gleichzeitig starten; Topics und Discovery-IDs überschneiden sich.
- **Sicherheit:** Retained Zustände können veraltet sein, keine Motorbestätigung und kein Ersatz für eine zertifizierte Rauchalarmierung.
