# Eltako2MQTT API Documentation

## Overview

This document provides technical information about the Eltako2MQTT bridge architecture and implementation.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Home Assistant                             │
│         (MQTT Discovery + Home Assistant UI)                 │
└──────────────────────────────────────────────────────────────┘
                            ↑↓ MQTT
┌──────────────────────────────────────────────────────────────┐
│                  MQTT Broker (Mosquitto)                      │
│           eltako/{SID}/set  ⟷  eltako/{SID}/state            │
└──────────────────────────────────────────────────────────────┘
                            ↑↓ MQTT
┌──────────────────────────────────────────────────────────────┐
│                  Eltako2MQTT Bridge                           │
│              (eltako2mqtt.py with asyncio)                   │
│                                                               │
│  - MQTT Client (paho-mqtt 2.1.0)                             │
│  - HTTP Client (aiohttp)                                     │
│  - Config Parser (PyYAML)                                    │
└──────────────────────────────────────────────────────────────┘
                            ↑↓ HTTP API
┌──────────────────────────────────────────────────────────────┐
│              Eltako MiniSafe2 (HTTP API)                      │
│                                                               │
│  GET /command?XC_FNC=GetStates        → Device polling       │
│  GET /command?XC_FNC=SendSC&...       → Device commands      │
│  {XC_SUC}JSON_DATA                   → Response format       │
└──────────────────────────────────────────────────────────────┘
                            ↑↓ EnOcean RF
┌──────────────────────────────────────────────────────────────┐
│           EnOcean Devices (Blinds, Switches, etc)            │
└──────────────────────────────────────────────────────────────┘
```

---

## Core Classes

### EltakoMiniSafe2Bridge

Main bridge class handling all operations.

#### Initialization

```python
def __init__(self, config_file: str):
    self.config          # Loaded YAML configuration
    self.mqtt_client     # paho-mqtt client instance
    self.session         # aiohttp session
    self.devices         # Dict[sid: str, device: Dict]
    self.loop            # asyncio event loop
    self.mqtt_connected  # Connection state flag (v1.1.0)
    self._recently_commanded_device  # Smart logging (v1.1.0)
```

#### Key Methods

**Connection Methods:**
- `setup_mqtt()` - Initialize and connect to MQTT broker
- `run()` - Main async loop

**Device Discovery:**
- `fetch_device_states()` - Poll MiniSafe2 for device states
- `publish_discovery()` - Send MQTT Discovery messages

**Command Processing:**
- `on_mqtt_message()` - Handle incoming MQTT messages
- `handle_device_command()` - Send command to MiniSafe2
- `build_command_url()` - Build HTTP API URL for command
- `update_device_state_immediate()` - Update local device state

**State Publishing:**
- `publish_device_state()` - Publish state to MQTT
- `poll_devices()` - Main polling loop

**Logging (v1.1.0):**
- `_is_recently_commanded()` - Check if device was recently commanded
- `_log_device_feedback()` - Smart feedback logging

---

## Data Structures

### Device Object

```python
{
    "sid": "01",                      # Short ID (device identifier)
    "data": "eltako_blind",            # Device type
    "adr": "0x12345678",               # EnOcean address
    "state": {
        # For blinds:
        "pos": 0,                      # Position 0-100
        "sync": true,                  # Sync status
        "rv": 1.5,                     # Reserve voltage
        "rt": 1000,                    # Response time (ms)
        
        # For switches:
        "state": "on",                 # State: on/off
        
        # For dimmers:
        "state": "on",                 # State: on/off
        "level": 100,                  # Level 0-100
        
        # For weather:
        "temperature": 22.5,           # Temperature °C
        "wind": 3.2,                   # Wind m/s
        "rain_state": false,           # Rain detected
        "illumination": 5000,          # Lux
        "s1": 5000,                    # East illumination
        "s2": 5200,                    # South illumination
        "s3": 4800,                    # West illumination
        
        # All devices:
        "rssiPercentage": 85           # Signal strength %
    }
}
```

### Configuration Object

```yaml
eltako:
  host: str              # MiniSafe2 IP address
  password: str          # HTTP API password
  poll_interval: int     # Polling interval in seconds

mqtt:
  host: str              # MQTT broker hostname
  port: int              # MQTT broker port
  username: str (opt)    # MQTT username
  password: str (opt)    # MQTT password
  client_id: str (opt)   # MQTT client ID

logging:
  level: str (opt)       # Log level: DEBUG, INFO, WARNING, ERROR
```

---

## MiniSafe2 HTTP API

### GetStates Endpoint

**Request:**
```
GET /command?XC_FNC=GetStates&XC_PASS={password}
```

**Response:**
```
{XC_SUC}{"devices":[{"sid":"01","data":"eltako_blind",...}]}
```

### SendSC (Send Command) Endpoint

**Request:**
```
GET /command?XC_FNC=SendSC&type=ENOCEAN&address={address}&data={command}&XC_PASS={password}
```

**Parameters:**
- `address` - EnOcean device address (URL-encoded)
- `data` - Command to send (e.g., "on", "off", "dimTo50")
- `XC_PASS` - API password (URL-encoded)

**Response on Success:**
```
{XC_SUC}
```

**Response on Error:**
```
{XC_ERR}Error message
```

---

## MQTT Topics & Payloads

### Subscribed Topics

```
eltako/+/set          # Device commands (incoming)
homeassistant/status  # HA startup notification
```

### Published Topics

**Device State:**
```
eltako/{SID}/state        # Current state/position
eltako/{SID}/brightness   # Brightness (dimmers only)
eltako/{SID}/rssi         # Signal strength
```

**Discovery:**
```
homeassistant/blind/eltako_blind_{SID}/config
homeassistant/switch/eltako_switch_{SID}/config
homeassistant/light/eltako_dimmer_{SID}/config
homeassistant/sensor/eltako_weather_{METRIC}_{SID}/config
```

### Discovery Payload Example

```json
{
  "name": "Eltako Blind 01",
  "unique_id": "eltako_blind_01",
  "device_class": "blind",
  "command_topic": "eltako/01/set",
  "position_topic": "eltako/01/state",
  "set_position_topic": "eltako/01/set",
  "position_closed": 100,
  "position_open": 0,
  "payload_open": "open",
  "payload_close": "close",
  "payload_stop": "stop",
  "device": {
    "identifiers": ["eltako_01"],
    "name": "Eltako 01",
    "model": "eltako_blind",
    "manufacturer": "Eltako"
  }
}
```

---

## Async Flow

### Main Event Loop

```python
async def run():
    # 1. Setup MQTT
    await setup_mqtt()
    
    # 2. Fetch initial device states
    devices = await fetch_device_states()
    
    # 3. Publish MQTT Discovery
    await publish_discovery()
    
    # 4. Publish initial states
    for sid, device in devices.items():
        await publish_device_state(sid, device)
    
    # 5. Start polling loop
    await poll_devices()  # Infinite loop
```

### Polling Loop

```python
async def poll_devices():
    while running:
        devices = await fetch_device_states()
        for sid, device in devices.items():
            # Update cached state
            self.devices[sid] = device
            
            # Publish state
            await publish_device_state(sid, device)
            
            # Log feedback if recently commanded (v1.1.0)
            self._log_device_feedback(sid, device)
        
        # Wait for next poll
        await asyncio.sleep(poll_interval)
```

### Command Processing

```python
def on_mqtt_message(client, userdata, msg):
    topic = msg.topic  # e.g., "eltako/01/set"
    payload = msg.payload.decode()  # e.g., "open"
    
    sid = topic.split("/")[1]  # Extract SID
    
    # Track command timing for logging
    if is_numeric(payload):
        _last_dim_command_time[sid] = time.monotonic()
        _recently_commanded_device = sid
    
    # Process command async
    asyncio.run_coroutine_threadsafe(
        handle_device_command(sid, payload),
        event_loop
    )
```

---

## Error Handling

### Connection Errors

```python
try:
    async with session.get(url) as response:
        if response.status == 200:
            # Success
        else:
            logger.error(f"HTTP error {response.status}")
except Exception as e:
    logger.error(f"Connection error: {e}")
```

### Validation Errors

```python
# Brightness validation (v1.1.0)
if level is None or not is_numeric(level):
    logger.warning(f"Invalid brightness: {level}")
    level = 0  # Graceful fallback

# Position validation
if position < 0 or position > 100:
    logger.warning(f"Position out of range: {position}")
    return None
```

---

## Logging System (v1.1.0)

### Configuration

```yaml
logging:
  level: DEBUG|INFO|WARNING|ERROR
```

### Smart Filtering

```python
def _log_device_feedback(self, sid, device):
    # Only log if:
    # 1. MQTT is connected
    # 2. Device was recently commanded
    # 3. Within timeout window (poll_interval + 60s)
    
    if not mqtt_connected:
        return
    
    if not _is_recently_commanded(sid):
        return
    
    logger.debug(f"Hardware feedback: {device_type} {sid}...")
```

### Log Levels

- `DEBUG` - Everything, including hardware feedback (filtered by above)
- `INFO` - Important events, connections
- `WARNING` - Warnings, invalid inputs
- `ERROR` - Errors, fatal issues

---

## Performance Considerations

### Polling Interval

Default: **5 seconds**

**Trade-offs:**
- Faster polling: More responsive but more network traffic
- Slower polling: Less traffic but slower state updates

**Recommendation:**
- 5-10 seconds: Most responsive
- 15-30 seconds: Good balance
- 60+ seconds: Minimal traffic, slower updates

### Memory Usage

- Device cache: ~1KB per device
- Command tracking: ~100 bytes per recently-commanded device
- MQTT connection: ~50KB for paho-mqtt client
- HTTP session: ~20KB for aiohttp session

**Typical:** 500KB-2MB for 10-50 devices

### CPU Usage

- Polling loop: ~1-5% (idle waiting)
- Command processing: <1% per command
- MQTT message handling: <1% per message

---

## Dependencies & Versions

### Core Dependencies

```
paho-mqtt==2.1.0       # MQTT client (VERSION2 API)
aiohttp==3.13.3+       # Async HTTP
PyYAML==6.0.3+         # Config parsing
```

### Python Version

- Minimum: Python 3.11
- Tested: Python 3.11.8

### Asyncio

- Uses modern asyncio patterns
- Thread-safe MQTT callbacks via `run_coroutine_threadsafe()`
- No blocking operations in event loop

---

## Extending the Bridge

### Adding Support for New Device Types

1. **Identify device type:** Check MiniSafe2 logs for "data" field
2. **Add to command handler:**
   ```python
   elif 'new_device' in device_type.lower():
       # Handle command
       cmd = parse_command(command)
       return self._build_url(address, cmd)
   ```
3. **Add to state publisher:**
   ```python
   elif 'new_device' in device_type.lower():
       # Publish state
       self.mqtt_client.publish(f"{base}/new_state", value)
   ```
4. **Add to discovery:**
   ```python
   elif 'new_device' in device_type.lower():
       config = {...device configuration...}
       topic = f"homeassistant/sensor/eltako_newdevice_{sid}/config"
       self.mqtt_client.publish(topic, json.dumps(config))
   ```

---

## Troubleshooting Guide

### Enable Debug Logging

```yaml
logging:
  level: DEBUG
```

### Monitor MQTT Messages

```bash
mosquitto_sub -v -t "eltako/#"
```

### Test MiniSafe2 Connectivity

```bash
curl "http://192.168.1.100/command?XC_FNC=GetStates&XC_PASS=password"
```

### Check Device Discovery

Look for in logs:
```
Publishing device with sid [01]
Published discovery for blind: homeassistant/cover/...
```

---

For more information, see:
- [README.md](README.md)
- [INSTALLATION.md](INSTALLATION.md)
- [MQTT_COMMANDS.md](MQTT_COMMANDS.md)
