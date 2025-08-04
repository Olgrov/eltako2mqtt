# Home Assistant Add-on: Eltako2MQTT

## Installation

Folgen Sie diesen Schritten für die Installation:

1. Navigieren Sie zu **Einstellungen** → **Add-ons** → **Add-on Store**
2. Klicken Sie oben rechts auf die drei Punkte → **Repositories**
3. Fügen Sie die Repository-URL hinzu und klicken Sie auf **Hinzufügen**
4. Suchen Sie nach "Eltako2MQTT" und klicken Sie darauf
5. Klicken Sie auf **INSTALLIEREN**

## Konfiguration

Die Add-on-Konfiguration erfolgt über die Benutzeroberfläche:

### Eltako-Konfiguration

- **Host**: IP-Adresse Ihres Eltako MiniSafe2 (z.B. `192.168.1.100`)
- **Password**: Zugangspasswort für das MiniSafe2 System
- **Poll Interval**: Abfrageintervall in Sekunden (1-300, Standard: 30)

### MQTT-Konfiguration

- **Host**: MQTT-Broker-Adresse (Standard: `core-mosquitto`)
- **Port**: MQTT-Port (Standard: 1883)
- **Username/Password**: Optional, falls MQTT-Authentifizierung erforderlich
- **Client ID**: MQTT-Client-Bezeichnung (Standard: `eltako2mqtt`)

### Logging

- **Level**: Detailgrad der Protokollierung (DEBUG, INFO, WARNING, ERROR)

## Verwendung

### Automatische Geräteerkennung

Das Add-on erkennt automatisch alle in Ihrem MiniSafe2 konfigurierten Geräte und macht sie über MQTT Discovery in Home Assistant verfügbar.

### Gerätesteuerung

Geräte können über Home Assistant oder direkt über MQTT-Befehle gesteuert werden:

#### Jalousien/Rollläden
- `OPEN` / `UP` - Öffnen
- `CLOSE` / `DOWN` - Schließen  
- `STOP` - Stoppen

#### Schalter
- `ON` - Einschalten
- `OFF` - Ausschalten
- `TOGGLE` - Umschalten

#### Dimmer
- `ON` - Einschalten
- `OFF` - Ausschalten
- `0-100` - Dimmlevel in Prozent

### MQTT-Topics

Das Add-on verwendet folgende Topic-Struktur:

- **Status**: `eltako/{SID}/state`
- **Befehle**: `eltako/{SID}/set`
- **RSSI**: `eltako/{SID}/rssi`
- **Zusätzliche Attribute**: Je nach Gerätetype

### Home Assistant Integration

Alle Geräte werden automatisch mit folgenden Eigenschaften erstellt:

- **Jalousien**: Als `cover` mit Position und Steuerung
- **Schalter**: Als `switch` mit Ein/Aus-Funktion
- **Dimmer**: Als `light` mit Dimm-Funktion
- **Wetterstation**: Als mehrere `sensor` für verschiedene Messwerte

**Hinweis zu Helligkeitssensoren (Illumination):**  
Die Werte der Sensoren `illumination_east`, `illumination_south` und `illumination_west` werden intern mit **1000 multipliziert**, um sie als Lux (lx) korrekt in Home Assistant anzuzeigen.
Alle vier Helligkeitssensoren (`illumination`, `illumination_east`, `illumination_south`, `illumination_west`) werden zudem als **Ganzzahlen (ohne Nachkommastellen)** ausgegeben.

## Fehlerbehebung

### Häufige Probleme

1. **Keine Geräte erkannt**
   - Prüfen Sie die IP-Adresse und das Passwort
   - Testen Sie den Zugriff über Browser: `http://IP/command?XC_FNC=GetStates&XC_PASS=password`

2. **MQTT-Verbindungsfehler**
   - Überprüfen Sie MQTT-Broker-Einstellungen
   - Stellen Sie sicher, dass der Mosquitto-Add-on läuft

3. **Befehle funktionieren nicht**
   - Prüfen Sie die Logs auf Fehlermeldungen
   - Aktivieren Sie DEBUG-Logging für detaillierte Informationen

### Log-Analyse

Die Logs finden Sie unter:
- **Add-ons** → **Eltako2MQTT** → **Log**

Für ausführliche Informationen setzen Sie das Log-Level auf "DEBUG".

## Support

Bei Problemen oder Fragen:
1. Prüfen Sie die Logs auf Fehlermeldungen
2. Überprüfen Sie die Netzwerkverbindung zum MiniSafe2
3. Stellen Sie sicher, dass alle erforderlichen Konfigurationen korrekt sind

