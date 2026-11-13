# Installation und Upgrade auf Eltako2MQTT v1.3.0

Diese Anleitung beschreibt das produktive Home-Assistant-Add-on.
Die Geräte müssen bereits im MiniSafe2 eingerichtet und vom Home-Assistant-System aus erreichbar sein.

## Voraussetzungen und Installation

- **Home Assistant:** Installation mit Add-on-Unterstützung und eingerichteter MQTT-Integration.
- **Broker:** Erreichbarer MQTT-Broker, beispielsweise das Mosquitto-Add-on.
- **MiniSafe:** IP/Hostname, Passwort und eingerichtete Geräte.
- **Netzwerk:** Zugriff vom Add-on auf MiniSafe-HTTP und den konfigurierten MQTT-Port.

Im Add-on Store unter Repositories `https://github.com/Olgrov/eltako2mqtt` hinzufügen und Eltako2MQTT installieren.
Anschließend die Konfiguration aus der [README](../README.md#konfiguration) übernehmen, Zugangsdaten ersetzen und das Add-on starten.
Es ist keine öffentliche Freigabe von MiniSafe, Broker oder Add-on-Port nötig.

## Konfigurationsreferenz

| Option | Standard | Bedeutung |
| --- | --- | --- |
| `eltako.host` | `192.168.1.100` im Installationsvorschlag | Tatsächliche MiniSafe-Adresse eintragen |
| `eltako.password` | leer | Pflichtfeld, MiniSafe-Passwort |
| `eltako.poll_interval` | 30 | Sekunden, Add-on-Schema 1–300, mindestens 30 empfohlen |
| `eltako.command_feedback_timeout` | 120 | Sekunden, Add-on-Schema 30–900 |
| `mqtt.host` | `core-mosquitto` | Pflichtfeld, tatsächlichen Broker eintragen |
| `mqtt.port` | 1883 | Broker-Port, Bereich 1–65535 |
| `mqtt.username`, `mqtt.password` | leer | Bei authentifiziertem Broker gemeinsam angeben |
| `mqtt.client_id` | `eltako2mqtt` | Eindeutige MQTT-Client-ID |
| `logging.level` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

Ein fehlender Feedback-Timeout wird zur Laufzeit mit 120 Sekunden ergänzt.
Vorhandene Pollingintervalle werden beibehalten; insbesondere alte Werte von 5 oder 15 Sekunden bitte bewusst auf mindestens 30 Sekunden umstellen.
Timeout und Polling sind unabhängig, und ein höherer Timeout erzeugt keine zusätzlichen Abfragen.

## Upgrade von einer Produktionsversion

1. Home-Assistant-Backup erstellen und aktuelle Add-on-Konfiguration sichern.
2. Add-on Store aktualisieren und Eltako2MQTT auf Version 1.3.0 aktualisieren.
3. `poll_interval` kontrollieren, bei Bedarf `command_feedback_timeout: 120` ergänzen und speichern.
4. Neues Image installieren/bauen und das Add-on starten. Ein Neustart eines alten Images installiert keine neue Version.
5. Startzeile, Discovery, Rollladenrichtung, Dimmer und Schalter prüfen.

Der produktive Name, Slug und die Standard-Client-ID bleiben `eltako2mqtt`.
Bestehende MQTT-Befehls-Topics und Discovery-IDs bleiben erhalten; Entitäten und Automatisierungen nicht löschen.
Discovery wird beim Start sowie bei `homeassistant/status = online` erneut veröffentlicht.

## Wechsel vom experimentellen Add-on

1. Test-Add-on stoppen und seinen Autostart deaktivieren.
2. Konfiguration in das produktive Add-on übertragen, insbesondere `poll_interval` und `command_feedback_timeout`.
3. Produktive Client-ID `eltako2mqtt` verwenden, sofern kein bewusst abweichender eindeutiger Wert nötig ist.
4. Produktive Version 1.3.0 installieren/bauen und starten.
5. Erst nach erfolgreicher Funktionsprüfung das alte lokale Test-Add-on optional entfernen.

Test- und Produktiv-Add-on dürfen nicht parallel laufen, auch nicht mit verschiedenen Client-IDs.
Sie teilen Command-Topics und Discovery-IDs und könnten Befehle doppelt ausführen.
Das Release enthält keinen experimentellen Startpfad mehr.

## Prüfung und Fehlersuche

- **Startprüfung:** `Eltako2MQTT 1.3.0; poll interval=30s; feedback timeout=120s` identifiziert den wirksamen produktiven Pfad.
- **Keine Geräte:** MiniSafe-Adresse, Passwort und Erreichbarkeit prüfen. Ein Start ohne Geräte beendet die Bridge; nach Behebung neu starten.
- **Keine Discovery:** MQTT-Integration, Broker-Zugang, `homeassistant/#` und `eltako/#` prüfen. Discovery-Daten sind retained.
- **Verspätete Position:** Unter `DEBUG` die `GetStates`-Startabstände und `Cover poll` prüfen. Alte Positionen werden absichtlich nicht durch ein Ziel ersetzt.
- **Timeout:** Längste Fahrt plus MiniSafe-Rückmeldeverzögerung berücksichtigen. Keine automatische Wiederholung und keine Stillstandsbestätigung.
- **Helligkeit fehlt:** Warnung mit SID und MiniSafe-Daten prüfen; der letzte gültige Helligkeitswert bleibt erhalten.
- **Sonderzeichen im Passwort:** Supervisor-JSON wird strukturiert nach YAML übertragen; Zugangsdaten nie in Logs oder Issue-Texte kopieren.

Der MiniSafe-Zugriff nutzt HTTP und der aktuelle MQTT-Client kein konfigurierbares TLS.
Beide Dienste deshalb nur in einem vertrauenswürdigen, geschützten Netzwerk betreiben.
Für Fehlerberichte Version, Gerätetyp, SID und bereinigte Debug-Logs an die [Issues](https://github.com/Olgrov/eltako2mqtt/issues) anhängen.

## Rückkehr zur vorherigen Version

Vor dem Update ein Backup erstellen und ein eventuelles lokales Checkout nicht ungesichert überschreiben.
Für einen Rückbau das gesicherte Add-on/Image wiederherstellen und seine Konfiguration kontrollieren.
Die vorherige Version veröffentlicht ihre Discovery erneut; die Bewegungsrückmeldung aus 1.3.0 steht dort nicht zur Verfügung.
