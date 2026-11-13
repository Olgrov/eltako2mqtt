# MQTT-Referenz für Eltako2MQTT v1.3.0

Geräte verwenden `eltako/{SID}/...`, wobei `{SID}` die vom MiniSafe gelieferte Gerätekennung ist.
Befehle werden auf `eltako/{SID}/set` gesendet und dürfen nicht retained sein, damit ein Neustart keine alten Fahrbefehle wiederholt.

## Rollläden und Jalousien

| Payload auf `/set` | Wirkung |
| --- | --- |
| `open`, `up` | Öffnen, MiniSafe `moveup`, Rohziel 0 |
| `close`, `down` | Schließen, MiniSafe `movedown`, Rohziel 100 |
| `stop` | Stop senden; keine unabhängige Motorbestätigung |
| `0` | Schließen, MiniSafe `moveTo100` |
| `100` | Öffnen, MiniSafe `moveTo0` |
| `25` | 25 Prozent offen, MiniSafe `moveTo75` |

Numerische Befehle verwenden die Home-Assistant-Skala 0=geschlossen und 100=offen.
Die Bridge invertiert einmal beim Erstellen des MiniSafe-Befehls; eigene Publisher dürfen nicht zusätzlich invertieren.

| Topic | Wert | Retained |
| --- | --- | --- |
| `eltako/{SID}/state` | MiniSafe-Rohposition 0=offen, 100=geschlossen | ja |
| `eltako/{SID}/movement` | `opening`, `closing`, `open`, `closed`, `stopped` | nein |
| `eltako/{SID}/sync` | Vom MiniSafe gelieferter Synchronisationswert | ja |
| `eltako/{SID}/rv` | MiniSafe-Rohwert `rv` | ja |
| `eltako/{SID}/rt` | MiniSafe-Rohwert `rt` | ja |
| `eltako/{SID}/rssi` | `rssiPercentage`, Prozent | ja |

Home Assistant erhält `position_closed: 100`, `position_open: 0` und `set_position_template: "{{ position }}"`.
Das numerische `/state` ist weder ein Motorzustand noch die Home-Assistant-Positionsskala, und ein `/pos`-Topic existiert nicht.

Nach erfolgreicher HTTP-Befehlsannahme wird nur die Bewegungsanzeige sofort publiziert.
Ein ausstehender Befehl hält seine angenommene Richtung über alte oder gegenläufige Positionsproben hinweg, bis Zielbestätigung, Ersatzbefehl oder Timeout erfolgt.
Jede gültige gepollte Position bleibt unverändert sichtbar.
Zielerkennung toleriert einen Prozentpunkt; am Teilziel wird `stopped` veröffentlicht, ohne die echte Position auf den Zielwert zu setzen.

Ohne ausstehenden Befehl wird Bewegung aus aufeinanderfolgenden Positionen abgeleitet.
Ein unveränderter Wert führt dann zu `stopped` bzw. `open`/`closed` am exakten Endpunkt; dies ist keine kontinuierliche Motorerfassung.
Der Feedback-Timeout beendet nur die Annahme, nicht die reale Fahrt.

## Schalter und Dimmer

| Gerät | Payload auf `/set` | Status |
| --- | --- | --- |
| Schalter einschließlich FSR14/FAE14 | `on`, `off`, `toggle` | `/state`: `on` oder `off` |
| Dimmer | `on`, `off`, numerisch 0–255 | `/state`: `on` oder `off`; `/brightness`: 0–255 |

Dimmerwerte werden mit `round(Wert * 100 / 255)` auf MiniSafe-Level umgerechnet.
128 entspricht ungefähr 50 Prozent; 50 ist nicht 50 Prozent, sondern ein Wert der 0–255-Skala.
Ein numerischer Wert, der auf Level 0 rundet, sendet `off`; ansonsten wird genau ein `dimToX` gesendet.
Ein direkt anschließendes `on` wird bei kürzlich empfangenem numerischem Befehl innerhalb von 1,5 Sekunden unterdrückt.

Home Assistant verwendet für Schalter/Dimmer `optimistic: true` und reale State-Topics.
Der UI-Zustand kann somit vorläufig reagieren, während externe MQTT-Abonnenten erst die regulär gepollten Zustände erhalten.
Ungültige oder fehlende Dimmerhelligkeit erzeugt keinen Ersatzwert 0; gültige Ein-/Aus-Werte und RSSI werden weiter veröffentlicht.
State, Brightness und RSSI sind retained.

## Wetterstationen und Rauchmelder

| Topic | Wert |
| --- | --- |
| `eltako/{SID}/wind` | Wind in m/s |
| `eltako/{SID}/rain` | Text `true` oder `false` |
| `eltako/{SID}/temperature` | Temperatur in °C |
| `eltako/{SID}/illumination` | Gerundete Beleuchtungsstärke in lx |
| `eltako/{SID}/illumination_east` | MiniSafe `s1` × 1000, gerundet, lx |
| `eltako/{SID}/illumination_south` | MiniSafe `s2` × 1000, gerundet, lx |
| `eltako/{SID}/illumination_west` | MiniSafe `s3` × 1000, gerundet, lx |
| `eltako/{SID}/smoke` | Rauchmelder: Text `true` oder `false` |
| `eltako/{SID}/rssi` | Signalstärke in Prozent, nicht dBm |

Diese Topics sind read-only und retained.
Rauchmelder veröffentlichen `/smoke`, `/temperature` und `/rssi`; Wetterstationen die Wetterwerte und `/rssi`.
RSSI wird veröffentlicht, aber nicht als eigener Discovery-Sensor erzeugt.
Rauch wird als Binary-Sensor mit `payload_on: "true"` und `payload_off: "false"` entdeckt; die MQTT-Payloads lauten nicht `on`/`off`.

## Discovery und Verfügbarkeit

- **Discovery:** Retained unter `homeassistant/{component}/{unique_id}/config`; IDs und Gerätetopics bleiben gegenüber der Produktion stabil.
- **Komponenten:** Cover, Switch, Light, sieben Wetter-Sensoren sowie Rauch-Binary-Sensor und Temperatur-Sensor.
- **Neuveröffentlichung:** Beim Start und bei `homeassistant/status` mit Payload `online`.
- **Verfügbarkeit:** Kein LWT-/Availability-Topic und keine Garantie, dass retained Zustände aktuell sind.

Polling erfolgt standardmäßig alle 30 Sekunden, gemessen zwischen den Starts von `GetStates`.
Lange Requests können den Abstand vergrößern; MiniSafe-Zugriffe sind serialisiert und ein Befehl kann einen laufenden HTTP-Request abwarten müssen.
Es gibt weder eine garantierte Rückmeldezeit noch einen zusätzlichen Poll pro Befehl.

## CLI- und Home-Assistant-Beispiele

```bash
mosquitto_sub -h BROKER -v -t 'eltako/#'
mosquitto_sub -h BROKER -v -t 'homeassistant/#'
mosquitto_pub -h BROKER -t eltako/01/set -m open
mosquitto_pub -h BROKER -t eltako/01/set -m 25
mosquitto_pub -h BROKER -t eltako/01/set -m stop
mosquitto_pub -h BROKER -t eltako/20/set -m toggle
mosquitto_pub -h BROKER -t eltako/13/set -m 128
```

Broker-Host und SID ersetzen sowie bei Bedarf Broker-Authentifizierung ergänzen.
In Home Assistant kann derselbe Befehl über `mqtt.publish` ohne retained Flag gesendet werden.

```yaml
action: mqtt.publish
data:
  topic: "eltako/01/set"
  payload: "100"
  retain: false
```

Für die normale Bedienung die automatisch entdeckten Entitäten verwenden.
Bei Fehlern [Installation/Diagnose](INSTALLATION.md) und [Feedback-Testplan](TESTING_OPTIMISTIC_STATE.md) konsultieren.
