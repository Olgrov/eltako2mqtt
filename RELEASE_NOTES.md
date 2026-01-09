# Eltako2MQTT Bridge - Release v1.1.0

**Release Date:** 2026-01-09

## 🎉 Overview

Major release featuring enhanced device handling, smart logging, and optimized polling for better responsiveness and reliability.

---

## ✨ What's New

### 🛡️ Defensive Brightness Handling

Improved `eltako_level_to_mqtt_brightness()` function with robust error handling:
- **Validates input** before conversion (0-100 range)
- **Handles edge cases:** None values, string inputs, over-limit values
- **Graceful fallback:** Automatically converts to 0 for invalid inputs
- **Informative logging:** Warns about invalid values instead of crashing
- **Prevents crashes:** No more runtime errors from bad brightness data

**Example:** Dimmer receives string `"abc"` → logs warning → uses 0 (off)

---

### 🎯 Position-Based Blind Commands

New position control for blinds with automatic inversion:
- **Position range:** 0 (open) to 100 (closed)
- **Home Assistant integration:** Use sliders to control blind position
- **Automatic inversion:** Eltako devices expect inverted position values
- **Smart state updates:** Waits for hardware feedback instead of guessing
- **Commands supported:**
  - Numeric: `moveTo0` (open) through `moveTo100` (closed)
  - Standard: `moveup`, `movedown`, `stop`

**Example:** Home Assistant sends position 25 → converted to `moveTo75` → blind opens 75%

---

### 📊 Enhanced Hardware Feedback Logging

Connection-aware, device-specific logging for better debugging:
- **MQTT connection check:** Only logs when broker is connected
- **Smart device filtering:** After you send a command, only that device's state is logged
- **Reduces noise:** No more logging all devices on every poll cycle
- **Debug-friendly:** Device type, state, and values clearly shown
- **Less spam:** Prevents overwhelming logs when disconnected

**Example:** You dim light #5 → only device #5 feedback is logged (not devices 1-20)

---

### ⏱️ Dynamic Command Timeout

Flexible timeout window based on your poll interval:
- **Calculation:** `poll_interval + 60 seconds`
- **Configurable:** Set via `config.yaml` → `eltako.poll_interval`
- **Default:** 5 second poll → 65 second timeout window
- **Use case:** Commands are tracked for this duration, then logged only if feedback arrives

**Example:**
```yaml
eltako:
  poll_interval: 5      # 5s poll + 60s = 65s timeout
  # OR for slower network:
  poll_interval: 15     # 15s poll + 60s = 75s timeout
```

---

### 🎛️ Configurable Logging Level

Control verbosity via `config.yaml`:
```yaml
logging:
  level: "DEBUG"   # DEBUG, INFO, WARNING, ERROR
```

**Levels:**
- `DEBUG` - Everything (hardware feedback for recently commanded devices only when MQTT connected)
- `INFO` - Important info (default)
- `WARNING` - Only warnings
- `ERROR` - Only errors

---

## 🚀 Performance Improvements

### Optimized Polling
- **Default poll_interval reduced:** 15 seconds → **5 seconds**
- **Benefit:** Faster device state updates, more responsive to commands
- **Backward compatible:** Set back to 15 if needed via config

```yaml
eltako:
  poll_interval: 5  # Fast (default)
  # OR
  poll_interval: 15  # Original speed
```

### Reduced Log Spam
- **Before:** Every device logged on every poll cycle
- **After:** Only recently commanded devices logged when MQTT connected
- **Result:** Clean, meaningful debug logs

---

## 📋 Complete Feature List

### Device Support
- ✅ **Dimmers** - with defensive brightness validation
- ✅ **Switches** - standard on/off/toggle
- ✅ **Blinds** - with position control and inversion
- ✅ **Weather Stations** - temperature, wind, rain, illumination

### Home Assistant Integration
- ✅ **MQTT Discovery** - Auto-discovery of all devices
- ✅ **Real-time Updates** - Connected via MQTT topics
- ✅ **Brightness Control** - For dimmers (0-255)
- ✅ **Position Control** - For blinds (0-100)
- ✅ **RSSI Monitoring** - Signal strength for each device

### Configuration
- ✅ **Flexible polling** - Configurable poll interval
- ✅ **Logging control** - Set log level
- ✅ **MQTT credentials** - Username/password support
- ✅ **Multi-language** - German/English support

---

## 🔄 Changes from v1.0.5

### New
- Defensive brightness handling for dimmers
- Position-based blind commands (0-100)
- Smart, connection-aware logging
- Dynamic command timeout calculation
- Configurable logging level
- Better error handling throughout

### Changed
- **Default poll_interval:** 15s → 5s (faster updates)
- **Blind payload:** UPPERCASE → lowercase (`open` not `OPEN`)
- **Logging:** More intelligent filtering
- **YAML generation:** Improved run.sh credential handling

### Fixed
- Dimmer crash risk from invalid brightness values
- Blind position inversion confusion
- Excessive logging when DEBUG enabled
- Hardware feedback noise in logs
- MQTT credential handling in addon

---

## 🛠️ Technical Details

### Code Changes
- Added `mqtt_connected` flag for connection tracking
- Added `_recently_commanded_device` for smart logging
- Added `_is_recently_commanded()` method for timeout checking
- Added `_log_device_feedback()` method for smart feedback logging
- Enhanced `eltako_level_to_mqtt_brightness()` with validation
- Enhanced `build_command_url()` with position support
- Enhanced `update_device_state_immediate()` with device parameter
- Improved `publish_discovery()` with lowercase payloads

### Files Modified
- `eltako2mqtt.py` - Main script with all enhancements
- `config.yaml` - Version updated, poll_interval default changed
- `run.sh` - Better YAML generation
- `CHANGELOG.md` - Detailed changelog

---

## 📖 Migration Guide

### Updating from v1.0.5

1. **No configuration changes needed** - Works with existing `config.yaml`

2. **Optional: Restore original poll interval**
   ```yaml
   eltako:
     poll_interval: 15  # If you prefer slower polling
   ```

3. **Optional: Enable DEBUG logging**
   ```yaml
   logging:
     level: "DEBUG"  # For detailed troubleshooting
   ```

4. **Blind commands in Home Assistant**
   - Payload changed: `OPEN` → `open`, `CLOSE` → `close`
   - UI sliders now correctly show blind position (0-100)
   - No manual reconfiguration needed

---

## ✅ Testing

Fully tested with:
- ✅ Multiple dimmer devices
- ✅ Blind controls with position commands
- ✅ Switch devices
- ✅ Weather station sensors
- ✅ MQTT Discovery in Home Assistant
- ✅ Connection state changes
- ✅ Invalid input handling
- ✅ DEBUG logging output

---

## 🔒 Compatibility

### Backward Compatibility
- ✅ **Fully backward compatible** - No breaking changes
- ✅ **Existing config.yaml works** - No updates required
- ✅ **No Home Assistant reconfig needed** - Auto-discovery handles it
- ✅ **Drop-in replacement** - Just update and go

### Dependencies
- `paho-mqtt` 2.1.0 - Modern MQTT client
- `aiohttp` 3.13.3+ - Async HTTP client
- `PyYAML` 6.0.3+ - Config parsing

---

## 🐛 Known Issues

None at this time. Please report any issues at:
https://github.com/Olgrov/eltako2mqtt/issues

---

## 🙏 Credits

- Original concept: [mediola2mqtt](https://github.com/andyboeh/mediola2mqtt)
- Enhancements: Community contributions via PR #9
- Tested with: Eltako MiniSafe2, Home Assistant, MQTT

---

## 📦 Installation

### Home Assistant
1. Add repository: `https://github.com/Olgrov/eltako2mqtt`
2. Install "Eltako2MQTT" add-on
3. Configure with your Eltako MiniSafe2 IP and MQTT broker
4. Start the add-on
5. Check logs for successful startup

### Docker / Standalone
```bash
git clone https://github.com/Olgrov/eltako2mqtt.git
cd eltako2mqtt
docker build -t eltako2mqtt .
docker run -v /path/to/config.yaml:/config.yaml eltako2mqtt python3 eltako2mqtt.py /config.yaml
```

---

**Happy automating! 🚀**
