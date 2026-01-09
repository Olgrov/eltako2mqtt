# MQTT Commands Reference

## Overview

This document provides a complete reference for all MQTT commands supported by Eltako2MQTT v1.1.0.

---

## Topic Structure

All commands follow this pattern:

```
eltako/{SID}/set
```

Where `{SID}` is the device ID (e.g., `01`, `11`, `13`).

### Find Your Device IDs

Check the add-on logs:
```
Found device 01: eltako_blind
Found device 11: eltako_switch
Found device 13: eltako_dimmer
```

---

## Device Types & Commands

### 🪟 Blinds / Rollos (eltako_blind, eltako_tf_blind)

#### Commands

| Command | Effect | MQTT Topic | Payload |
|---------|--------|-----------|----------|
| Open | Open fully (position 0%) | `eltako/{SID}/set` | `open` |
| Close | Close fully (position 100%) | `eltako/{SID}/set` | `close` |
| Stop | Stop current movement | `eltako/{SID}/set` | `stop` |
| Move Up | Move towards open | `eltako/{SID}/set` | `moveup` |
| Move Down | Move towards closed | `eltako/{SID}/set` | `movedown` |
| Set Position | Move to specific position (0-100%) | `eltako/{SID}/set` | `0` to `100` |

#### Examples

**Open blind completely:**
```bash
mosquitto_pub -t "eltako/01/set" -m "open"
```

**Close blind completely:**
```bash
mosquitto_pub -t "eltako/01/set" -m "close"
```

**Move to 50% position (half open):**
```bash
mosquitto_pub -t "eltako/01/set" -m "50"
```

**Move up slightly:**
```bash
mosquitto_pub -t "eltako/01/set" -m "moveup"
```

**Stop movement:**
```bash
mosquitto_pub -t "eltako/01/set" -m "stop"
```

#### Status Topics

| Topic | Value | Meaning |
|-------|-------|----------|
| `eltako/{SID}/state` | 0-100 | Current blind position (%) |
| `eltako/{SID}/sync` | true/false | Synchronization status |
| `eltako/{SID}/rssi` | 0-100 | Signal strength (%) |
| `eltako/{SID}/rv` | number | Reserve voltage |
| `eltako/{SID}/rt` | number | Response time |

#### Position Details (v1.1.0)

- Position is automatically inverted for Eltako compatibility
- 0% = Fully open
- 100% = Fully closed
- Home Assistant UI shows correct position
- State update waits for hardware feedback (not immediate)

---

### 🔌 Switches (eltako_switch, eltako_tf_switch)

#### Commands

| Command | Effect | MQTT Topic | Payload |
|---------|--------|-----------|----------|
| On | Turn on | `eltako/{SID}/set` | `on` |
| Off | Turn off | `eltako/{SID}/set` | `off` |
| Toggle | Toggle state | `eltako/{SID}/set` | `toggle` |

#### Examples

**Turn on:**
```bash
mosquitto_pub -t "eltako/11/set" -m "on"
```

**Turn off:**
```bash
mosquitto_pub -t "eltako/11/set" -m "off"
```

**Toggle (on→off or off→on):**
```bash
mosquitto_pub -t "eltako/11/set" -m "toggle"
```

#### Status Topics

| Topic | Value | Meaning |
|-------|-------|----------|
| `eltako/{SID}/state` | on/off | Current switch state |
| `eltako/{SID}/rssi` | 0-100 | Signal strength (%) |

---

### 💡 Dimmers (eltako_dimmer, eltako_tf_dimmer)

#### Commands

| Command | Effect | MQTT Topic | Payload |
|---------|--------|-----------|----------|
| On | Turn on (full brightness) | `eltako/{SID}/set` | `on` |
| Off | Turn off | `eltako/{SID}/set` | `off` |
| Set Brightness | Set brightness 0-100% | `eltako/{SID}/set` | `0` to `100` |
| Set Brightness | Set brightness 0-255 scale | `eltako/{SID}/set` | `0` to `255` |

#### Examples

**Turn on (full brightness):**
```bash
mosquitto_pub -t "eltako/13/set" -m "on"
```

**Turn off:**
```bash
mosquitto_pub -t "eltako/13/set" -m "off"
```

**Dim to 50% brightness:**
```bash
mosquitto_pub -t "eltako/13/set" -m "50"
```

**Dim to brightness level 200 (0-255 scale):**
```bash
mosquitto_pub -t "eltako/13/set" -m "200"
```

**Dim to 25% brightness:**
```bash
mosquitto_pub -t "eltako/13/set" -m "25"
```

#### Status Topics

| Topic | Value | Meaning |
|-------|-------|----------|
| `eltako/{SID}/state` | on/off | Current dimmer state |
| `eltako/{SID}/brightness` | 0-255 | Brightness level (0-255 scale) |
| `eltako/{SID}/rssi` | 0-100 | Signal strength (%) |

#### Brightness Handling (v1.1.0)

- Supports both 0-100% and 0-255 scales
- Automatic scale detection
- Defensive validation prevents crashes
- Invalid values gracefully fallback to 0
- Example: `"invalid_value"` → logs warning, uses 0 (off)

---

### 🌤️ Weather Stations (eltako_weather)

Weather stations are **read-only** - no commands can be sent.

#### Status Topics (Read-Only)

| Topic | Value | Unit | Meaning |
|-------|-------|------|----------|
| `eltako/{SID}/temperature` | number | °C | Ambient temperature |
| `eltako/{SID}/wind` | number | m/s | Wind speed |
| `eltako/{SID}/rain` | true/false | - | Rain detected |
| `eltako/{SID}/illumination` | number | lx | Total illumination |
| `eltako/{SID}/illumination_east` | number | lx | East-facing illumination |
| `eltako/{SID}/illumination_south` | number | lx | South-facing illumination |
| `eltako/{SID}/illumination_west` | number | lx | West-facing illumination |
| `eltako/{SID}/rssi` | 0-100 | - | Signal strength (%) |

#### Notes

- All values update automatically at `poll_interval` (default: 5 seconds)
- Illumination values are in Lux (lx)
- Wind speed in meters per second (m/s)
- Temperature in Celsius (°C)
- Rain is a boolean (true/false or 1/0)

---

## General Topics

### All Devices

**Signal Strength (RSSI):**
```
eltako/{SID}/rssi
```

Value: 0-100 (percentage)

Example:
```bash
mosquitto_sub -t "eltako/+/rssi"
# Output: eltako/01/rssi 85
```

---

## Testing Commands

### Using Home Assistant Developer Tools

1. Go to **Developer Tools** → **MQTT**
2. Under "Publish a packet":
   - **Topic:** `eltako/01/set`
   - **Payload:** `open`
   - Click **Publish**

### Using Command Line (mosquitto_pub)

**Open blind:**
```bash
mosquitto_pub -h 192.168.1.100 -t "eltako/01/set" -m "open"
```

**Turn on light:**
```bash
mosquitto_pub -h 192.168.1.100 -t "eltako/13/set" -m "on"
```

### Monitoring State Changes

**Watch all device updates:**
```bash
mosquitto_sub -h 192.168.1.100 -t "eltako/#"
```

**Watch specific device:**
```bash
mosquitto_sub -h 192.168.1.100 -t "eltako/01/#"
```

---

## Response Times

Typical response times after command:

| Device Type | Feedback Time | Notes |
|-------------|---------------|-------|
| Blind | 0.5-2 seconds | Depends on movement speed |
| Switch | <1 second | Usually immediate |
| Dimmer | <1 second | Usually immediate |
| Weather | Up to 5 seconds | Depends on poll_interval |

---

## Error Handling (v1.1.0)

### Invalid Commands

Invalid payloads are silently ignored:

```bash
# These are ignored:
mosquitto_pub -t "eltako/01/set" -m "invalid"
mosquitto_pub -t "eltako/13/set" -m "999"
mosquitto_pub -t "eltako/13/set" -m "abc"
```

Check logs (set to DEBUG) to see warnings.

### Connection Issues

If commands don't work:
1. Check MQTT connection in Home Assistant logs
2. Verify device ID is correct
3. Ensure MiniSafe2 is responsive
4. Check command payload is valid
5. Enable DEBUG logging for details

---

## Home Assistant Automation Examples

### Automate Blind Opening at Sunrise

```yaml
automation:
  - alias: "Open blinds at sunrise"
    trigger:
      platform: sun
      event: sunrise
    action:
      service: mqtt.publish
      data:
        topic: "eltako/01/set"
        payload: "open"
```

### Dim Light Based on Time

```yaml
automation:
  - alias: "Evening dimming"
    trigger:
      platform: time
      at: "18:00:00"
    action:
      service: mqtt.publish
      data:
        topic: "eltako/13/set"
        payload: "50"  # 50% brightness
```

### Turn Off When Away

```yaml
automation:
  - alias: "Turn off when away"
    trigger:
      platform: state
      entity_id: group.all_people
      to: "not_home"
    action:
      service: mqtt.publish
      data:
        topic: "eltako/11/set"
        payload: "off"
```

---

## Troubleshooting Commands

### Test MQTT Connection

```bash
# Subscribe to all eltako messages
mosquitto_sub -t "eltako/#" -v

# In another terminal, publish a test command
mosquitto_pub -t "eltako/01/set" -m "open"

# You should see: eltako/01/set open
```

### Monitor Command Execution

1. Enable DEBUG logging in add-on configuration
2. Restart add-on
3. Send a command
4. Check logs for:
   - "Command successful for"
   - "Hardware feedback for"

### Check Device Responsiveness

```bash
# Monitor device state
mosquitto_sub -t "eltako/01/state" -v

# Send a command
mosquitto_pub -t "eltako/01/set" -m "50"

# You should see state change within 5-10 seconds:
# eltako/01/state 50
```

---

For more help, see [INSTALLATION.md](INSTALLATION.md) or [README.md](README.md).
