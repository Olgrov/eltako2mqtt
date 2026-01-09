# Eltako2MQTT Installation & Configuration Guide

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [First Steps](#first-steps)
- [Troubleshooting](#troubleshooting)

---

## Requirements

### Hardware
- **Home Assistant** (any supported hardware: Raspberry Pi, Intel NUC, etc.)
- **MQTT Broker** (e.g., Mosquitto)
- **Eltako MiniSafe2** device connected to the same network
- Network connectivity between all components

### Software
- Home Assistant 2024.1 or newer
- MQTT integration installed and configured in Home Assistant
- Eltako MiniSafe2 properly configured with your EnOcean devices

---

## Installation

### Step 1: Add the Repository

1. Open Home Assistant
2. Go to **Settings** → **Add-ons** → **Add-on Store**
3. Click the **⋮** (three dots) button in the top right
4. Select **Repositories**
5. Add this URL: `https://github.com/Olgrov/eltako2mqtt`
6. Click **Create**
7. Refresh the page (F5 or Ctrl+R)

### Step 2: Install the Add-on

1. Search for "Eltako2MQTT" in the Add-on Store
2. Click on the result
3. Click **INSTALL**
4. Wait for the installation to complete (may take 2-5 minutes)

### Step 3: Configure the Add-on

See [Configuration Section](#configuration) below.

### Step 4: Start the Add-on

1. Click **START**
2. Check the **Logs** tab - you should see:
   ```
   Starting Eltako2MQTT Bridge...
   Eltako Host: 192.168.1.100
   MQTT Host: core-mosquitto:1883
   Logging Level: INFO
   Starting Python bridge...
   ```

### Step 5: Verify Device Discovery

1. Wait 10-15 seconds for the bridge to discover devices
2. Go to **Settings** → **Devices & Services** → **MQTT**
3. You should see discovered devices appearing
4. Devices should also be available in Home Assistant automations

---

## Configuration

### Basic Configuration

1. In the Add-on page, click **CONFIGURATION** tab
2. Fill in the required fields:

#### Eltako Settings
- **Host**: IP address of your Eltako MiniSafe2 (e.g., `192.168.1.100`)
  - Find this: Open MiniSafe2 web interface → Network settings
- **Password**: HTTP API password for MiniSafe2
  - Find this: MiniSafe2 documentation or web interface
- **Poll Interval**: How often to check device states (seconds)
  - Recommended: **5** (default)
  - Range: 1-300 seconds

#### MQTT Settings
- **Host**: MQTT broker hostname
  - Default: `core-mosquitto` (Home Assistant's built-in broker)
  - Alternative: IP address or hostname of external broker
- **Port**: MQTT broker port
  - Default: `1883`
  - Secure: `8883`
- **Username** (optional): MQTT username if authentication required
- **Password** (optional): MQTT password if authentication required
- **Client ID**: Unique identifier for this connection
  - Default: `eltako2mqtt`

#### Logging Settings
- **Level**: How verbose the logging is
  - `INFO` (default) - Important messages only
  - `DEBUG` - Detailed debugging information
  - `WARNING` - Only warnings and errors
  - `ERROR` - Only errors

### Example Configuration

```yaml
eltako:
  host: "192.168.1.100"
  password: "your_password_here"
  poll_interval: 5

mqtt:
  host: "core-mosquitto"
  port: 1883
  username: ""
  password: ""
  client_id: "eltako2mqtt"

logging:
  level: "INFO"
```

### Advanced Configuration

#### Using External MQTT Broker

If you want to use an external MQTT broker instead of Home Assistant's built-in one:

```yaml
mqtt:
  host: "192.168.1.50"        # IP of your MQTT broker
  port: 1883
  username: "mqttuser"
  password: "mqttpassword"
  client_id: "eltako2mqtt"
```

#### Slower Polling for Low Bandwidth

If you have a slow network connection:

```yaml
eltako:
  poll_interval: 15           # Check every 15 seconds instead of 5
```

#### Enable Debug Logging

For troubleshooting:

```yaml
logging:
  level: "DEBUG"              # Detailed logging
```

---

## First Steps

### 1. Verify Connection

After starting the add-on:
1. Go to **Settings** → **Add-ons** → **Eltako2MQTT** → **Logs**
2. Look for these messages:
   - `Connected to MQTT broker` ✅
   - `Found device` (for each device) ✅
   - `Published discovery` ✅

If you see errors, check [Troubleshooting](#troubleshooting) section.

### 2. Find Your Device IDs

In the logs, look for lines like:
```
Found device 01: eltako_blind
Found device 11: eltako_switch
Found device 13: eltako_dimmer
```

These IDs (01, 11, 13) are used for controlling devices via MQTT.

### 3. Control a Device

To test, send an MQTT command:

**Using Home Assistant Developer Tools:**
1. Go to **Developer Tools** → **MQTT**
2. Under **Publish a packet**:
   - Topic: `eltako/01/set`
   - Payload: `open`
   - Click **Publish**

Your blind should open (if device 01 is a blind)!

### 4. Verify Home Assistant Integration

1. Go to **Settings** → **Devices & Services** → **MQTT**
2. You should see devices like:
   - "Eltako Blind 01"
   - "Eltako Switch 11"
   - "Eltako Dimmer 13"
   - etc.

3. Click on a device to control it from the UI

---

## Troubleshooting

### Issue: Add-on won't start

**Error: "Connection refused"**
- ❌ MiniSafe2 is offline or unreachable
- ✅ Check if MiniSafe2 IP address is correct
- ✅ Ping the device: Open terminal and type `ping 192.168.1.100` (use your IP)
- ✅ Check if MiniSafe2 is on the same network

**Error: "Authentication failed"**
- ❌ Wrong MiniSafe2 password
- ✅ Double-check the password in configuration
- ✅ Test in MiniSafe2 web interface to confirm password works

### Issue: No devices discovered

**Check 1: Are devices configured in MiniSafe2?**
- ✅ Open MiniSafe2 web interface
- ✅ Check if EnOcean devices are listed
- ✅ Devices must be taught-in to MiniSafe2

**Check 2: Enable DEBUG logging**
1. Set `logging.level` to `DEBUG`
2. Restart the add-on
3. Check logs for:
   - `Fetching device states...`
   - `Found device...`
   - If you see `No devices found`, check MiniSafe2 configuration

**Check 3: MQTT connection**
- ✅ Make sure MQTT broker is running
- ✅ Check MQTT hostname and port are correct
- ✅ In Home Assistant, go to **Settings** → **Devices & Services** → **MQTT**
  - Should show "Connected" in green

### Issue: Devices appear but don't respond

**Check 1: MQTT Topics**
1. Open **Developer Tools** → **MQTT**
2. Subscribe to: `eltako/#`
3. You should see messages like:
   - `eltako/01/state 0` (blind position)
   - `eltako/11/state on` (switch state)
   - Updates every 5 seconds

**Check 2: Send a command**
```
Topic: eltako/01/set
Payload: open
```

You should see in logs:
```
Command successful for 01: open
Hardware feedback for blind 01: position=0%
```

**Check 3: Check Home Assistant logs**
- Go to **Settings** → **System** → **Logs**
- Search for MQTT errors
- Check for connection issues

### Issue: Excessive logging output

Too many messages in the logs?
- ✅ Set `logging.level` to `INFO` or `WARNING`
- ℹ️ In v1.1.0: DEBUG logging is smart-filtered (only logs recently commanded devices when MQTT connected)

### Issue: Commands don't work

**Check 1: Correct device ID?**
- ✅ Check logs for "Found device 01..."
- ✅ Make sure you're using the right ID

**Check 2: Correct payload?**
- Blinds: `open`, `close`, `stop`, or `0-100` (position)
- Switches: `on`, `off`, `toggle`
- Dimmers: `on`, `off`, or `0-100` (brightness %)

**Check 3: MiniSafe2 responding?**
- ✅ Try opening MiniSafe2 web interface
- ✅ Manually control the device
- ✅ Check if MiniSafe2 shows any errors

### Getting Help

If nothing works:

1. **Collect debug info**
   - Set logging to DEBUG
   - Restart add-on
   - Wait 2 minutes
   - Copy all logs

2. **Check the GitHub issues**
   - https://github.com/Olgrov/eltako2mqtt/issues
   - Search for similar problems

3. **Create a new issue**
   - Include:
     - Your configuration (hide passwords)
     - Logs from the add-on
     - What you tried
     - Home Assistant version
     - MiniSafe2 firmware version

---

## Version Information

This guide is for **Eltako2MQTT v1.1.0** and later.

For previous versions, see the [CHANGELOG](CHANGELOG.md).
