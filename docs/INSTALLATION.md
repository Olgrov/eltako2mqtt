<a name="installation-und-upgrade-auf-eltako2mqtt-v130"></a>

# Installation und Upgrade auf Eltako2MQTT v1.4.0

Diese Anleitung beschreibt das produktive Home-Assistant-Add-on.
Die Geräte müssen bereits im MiniSafe2 eingerichtet und vom Home-Assistant-System aus erreichbar sein.

## Voraussetzungen und Installation

- **Home Assistant:** Installation mit Add-on-Unterstützung und eingerichteter MQTT-Integration.
- **Architektur:** Nur `amd64` oder `aarch64`; für 32-Bit-Systeme siehe den [Legacy-Hinweis](#32-bit-systeme-und-letzter-legacy-stand).
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
2. Auf amd64 oder aarch64 den Add-on Store aktualisieren und Eltako2MQTT auf Version 1.4.0 aktualisieren.
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
4. Auf einem unterstützten 64-Bit-System die produktive Version 1.4.0 installieren/bauen und starten.
5. Erst nach erfolgreicher Funktionsprüfung das alte lokale Test-Add-on optional entfernen.

Test- und Produktiv-Add-on dürfen nicht parallel laufen, auch nicht mit verschiedenen Client-IDs.
Sie teilen Command-Topics und Discovery-IDs und könnten Befehle doppelt ausführen.
Das Release enthält keinen experimentellen Startpfad mehr.

## 32-Bit-Systeme und letzter Legacy-Stand

`armhf`, `armv7` und `i386` werden ab v1.4.0 nicht mehr unterstützt.
Das unveränderte [Release v1.3.0](https://github.com/Olgrov/eltako2mqtt/releases/tag/v1.3.0) und der [Quellstand v1.3.0](https://github.com/Olgrov/eltako2mqtt/tree/v1.3.0) bleiben als letzte veröffentlichte 32-Bit-Version erhalten.

- **Bestehendes 32-Bit-System:** Ein gesichertes v1.3.0-Image beziehungsweise Backup kann vorerst weiterverwendet werden; keine Aktualisierung auf v1.4.0 erzwingen.
- **Manuelle lokale Installation:** Genau den Tag `v1.3.0` verwenden, nicht `main` oder den v1.4.0-Quellstand. Historische Installationshinweise sind im getaggten Quellstand enthalten.
- **Keine Wartungszusage:** Das Aufbewahren des Tags bedeutet keine weitere Pflege oder Sicherheitsupdates für die alte Plattform.
- **Migration:** Vollständiges Home-Assistant-Backup herunterladen, ein unterstütztes 64-Bit-System installieren und das Backup wiederherstellen; danach v1.4.0 installieren/aktualisieren.
- **64-Bit-fähige Hardware:** Beispielsweise können Raspberry Pi 3/4 trotz bisherigem 32-Bit-OS auf ein 64-Bit-OS umgestellt werden; reine 32-Bit-Hardware muss ersetzt werden.

Home Assistant selbst unterstützt diese 32-Bit-Architekturen nicht mehr und stellt dafür keine regulären Komponenten-/Add-on-Updates bereit ([offizieller Supporthinweis](https://www.home-assistant.io/more-info/unsupported/system_architecture/)).
Bestehende Entitäts-IDs, MQTT-Topics und Add-on-Konfiguration bleiben nach einer 64-Bit-Migration erhalten; Test- und Produktiv-Bridge dürfen weiterhin nicht gleichzeitig laufen.

## Prüfung und Fehlersuche

- **Startprüfung:** `Eltako2MQTT 1.4.0; poll interval=30s; feedback timeout=120s` identifiziert den wirksamen produktiven Pfad.
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
Beim Rückbau auf v1.3.0 bleibt die dort bereits enthaltene Bewegungsrückmeldung verfügbar; die Plattformmodernisierung aus v1.4.0 entfällt.
Die alte Laufzeit ist nur ein historischer Rückfallstand und erhält dadurch keine neue Sicherheits- oder Supportzusage.
