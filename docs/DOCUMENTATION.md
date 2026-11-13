<a name="eltako2mqtt-v130-dokumentation"></a>

# Eltako2MQTT v1.4.0 Dokumentation

Die Dokumentation beschreibt den produktiven Stand mit Zustandsrückmeldung und `paho-mqtt` 2.2.0.
v1.4.0 unterstützt nur amd64 und aarch64; v1.3.0 bleibt als letzte veröffentlichte 32-Bit-Version erhalten.
Historische Releaseabschnitte sind als Historie zu lesen, nicht als aktuelle Konfigurationsempfehlung.

## Einstieg und Betrieb

- **[README](../README.md):** Funktionen, Gerätetypen, Konfiguration und zentrale Grenzen.
- **[Installation und Upgrade](INSTALLATION.md):** Produktionsupdate, 32-/64-Bit-Migration, letzter Legacy-Stand, Wechsel vom Test-Add-on, Diagnose und Rückbau.
- **[MQTT-Referenz](MQTT_COMMANDS.md):** Command-Payloads, Status-Topics, Positionsskalen, Discovery und CLI-Beispiele.
- **[Release Notes](RELEASE_NOTES.md):** Änderungen in 1.4.0, Migrationshinweise und frühere Releases.
- **[Changelog](../CHANGELOG.md):** Technische Änderungshistorie.

## Entwicklung und Prüfung

- **[Architektur/API](API.md):** Produktiver Einstieg, Basisklasse, Feedback-Modul, MiniSafe-Protokoll und Tests.
- **[Feedback-Testplan](TESTING_OPTIMISTIC_STATE.md):** Automatisierte und praktische Regressionen für Produktion und Migration.
- **[Experimentelle Historie](../CHANGELOG.md#125-test3---2026-10-30):** Im Haupt-Changelog zusammengeführt; die alte Dokument-URL bleibt als Verweisseite erhalten.

## Wichtige Verträge

- **Version:** 1.4.0, Name/Slug `eltako2mqtt`, Standard-MQTT-Client-ID `eltako2mqtt`.
- **Plattform:** Python 3.15/Alpine 3.24 auf amd64 und aarch64; v1.3.0 ist der unveränderte historische 32-Bit-Stand.
- **Polling:** Standard 30 Sekunden; kleinere bestehende Werte werden beibehalten, aber nicht empfohlen.
- **Feedback:** Optionaler unabhängiger Timeout, Standard 120 Sekunden; keine zusätzlichen Polls oder Retries.
- **Position:** MQTT-Befehl und Home Assistant 0=geschlossen/100=offen, MQTT-Rohstatus genau umgekehrt.
- **Betrieb:** Produktiv- und Test-Add-on nie gleichzeitig starten; Topics und Discovery-IDs überschneiden sich.
- **Sicherheit:** Retained Zustände können veraltet sein, keine Motorbestätigung und kein Ersatz für eine zertifizierte Rauchalarmierung.
