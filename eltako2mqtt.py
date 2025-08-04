#!/usr/bin/env python3

"""
Eltako MiniSafe2 MQTT Bridge

Dimmerbefehle exakt: dimToX, on, off – keine Doppelbefehle!
"""

import asyncio
import aiohttp
import json
import logging
import signal
import sys
import yaml
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from urllib.parse import quote_plus
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EltakoMiniSafe2Bridge:
    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self.mqtt_client: Optional[mqtt.Client] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.devices: Dict[str, Any] = {}
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._last_dim_command_time: Dict[str, float] = {}

        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.eltako_config = self.config['eltako']
        self.mqtt_config = self.config['mqtt']
        self.base_url = f"http://{self.eltako_config['host']}/command"
        self.password = self.eltako_config['password']
        self.poll_interval = self.eltako_config.get('poll_interval', 15)

    def load_config(self, config_file: str) -> Dict[str, Any]:
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def setup_mqtt(self):
        self.mqtt_client = mqtt.Client(client_id=self.mqtt_config.get('client_id', 'eltako2mqtt'))
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect

        if self.mqtt_config.get('username') and self.mqtt_config.get('password'):
            self.mqtt_client.username_pw_set(
                self.mqtt_config['username'],
                self.mqtt_config['password']
            )
        try:
            self.mqtt_client.connect(
                self.mqtt_config['host'],
                self.mqtt_config.get('port', 1883),
                60
            )
            self.mqtt_client.loop_start()
            logger.info("MQTT client connected")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
            client.subscribe("eltako/+/set")
            client.subscribe("homeassistant/status")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        logger.debug(f"Received MQTT message: {topic} = {payload}")
        if topic == "homeassistant/status" and payload == "online":
            if self.loop:
                asyncio.run_coroutine_threadsafe(self.publish_discovery(), self.loop)
            else:
                logger.error("No event loop set for scheduling publish_discovery")
            return

        if topic.startswith("eltako/") and topic.endswith("/set"):
            sid = topic.split("/")[1]
            if self.loop:
                now = time.monotonic()
                # Sperre 'on' Befehl, wenn innerhalb 1.5 Sekunden zuvor dimToX gesendet wurde
                if payload.strip().lower() == 'on':
                    last_dim_time = self._last_dim_command_time.get(sid, 0)
                    if (now - last_dim_time) < 1.5:
                        logger.info(f"Ignoring 'on' command for {sid} due to recent dimToX command")
                        return
                else:
                    # Prüfe, ob Payload numerisch (dim-Level)
                    if self.is_numeric(payload):
                        self._last_dim_command_time[sid] = now

                asyncio.run_coroutine_threadsafe(self.handle_device_command(sid, payload), self.loop)

    def on_mqtt_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected from MQTT broker: {rc}")

    @staticmethod
    def is_numeric(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    async def handle_device_command(self, sid: str, command: str):
        logger.info(f"Handling command for {sid}: '{command}'")
        if sid not in self.devices:
            logger.warning(f"Unknown device SID: {sid}")
            return

        device = self.devices[sid]
        url = self.build_command_url(device, command)
        if not url:
            logger.warning(f"Ignoring unsupported command: {command}")
            return

        try:
            async with self.session.get(url) as response:
                text = await response.text()
                if response.status == 200 and "{XC_SUC}" in text:
                    logger.info(f"Command successful for {sid}: {command}")
                    await self.update_device_state_immediate(sid, command)
                else:
                    logger.error(f"Command failed for {sid} ({command}): {text}")
        except Exception as e:
            logger.error(f"Error sending command to {sid}: {e}")

    def build_command_url(self, device: Dict[str, Any], command: str) -> Optional[str]:
        device_type = device.get('data', '')
        address = device.get('adr', '')
        if not device_type or not address:
            return None
        cmd_lower = command.strip().lower()

        if 'dimmer' in device_type.lower():
            if cmd_lower == "on":
                cmd = "on"
            elif cmd_lower == "off":
                cmd = "off"
            else:
                try:
                    val = float(command)
                    if 0 <= val <= 255:
                        level = round(val * 100 / 255)
                    elif 0 <= val <= 100:
                        level = int(val)
                    else:
                        logger.warning(f"Dimmer value out of range: {val}")
                        return None
                    if level == 0:
                        cmd = "off"
                    else:
                        cmd = f"dimTo{level}"
                except Exception:
                    logger.warning(f"Invalid dimmer numeric command: {command}")
                    return None
            return self._build_url(address, cmd)
        elif 'blind' in device_type.lower():
            c = command.upper()
            if c in ['OPEN', 'UP']:
                cmd = 'up'
            elif c in ['CLOSE', 'DOWN']:
                cmd = 'down'
            elif c == 'STOP':
                cmd = 'stop'
            else:
                return None
            return self._build_url(address, cmd)
        elif 'switch' in device_type.lower():
            c = command.lower()
            if c in ['on', 'off']:
                cmd = c
            elif c == 'toggle':
                cmd = 'toggle'
            else:
                return None
            return self._build_url(address, cmd)
        else:
            logger.warning(f"Unknown device type {device_type} for command.")
            return None

    def _build_url(self, address: str, cmd_data: str) -> str:
        return f"{self.base_url}?XC_FNC=SendSC&type=ENOCEAN&address={address}&data={cmd_data}&XC_PASS={quote_plus(self.password)}"

    async def update_device_state_immediate(self, sid: str, command: str):
        if sid not in self.devices:
            return

        device = self.devices[sid]
        device_type = device.get('data', '')
        cmd_lower = command.strip().lower()
        val_numeric = None

        try:
            val_numeric = float(command)
            is_numeric = True
        except Exception:
            is_numeric = False

        if 'dimmer' in device_type.lower():
            if cmd_lower == 'on':
                device['state']['state'] = 'on'
                if device['state'].get('level', 0) == 0:
                    device['state']['level'] = 100
            elif cmd_lower == 'off':
                device['state']['state'] = 'off'
                device['state']['level'] = 0
            elif is_numeric:
                if 0 <= val_numeric <= 255:
                    level = round(val_numeric * 100 / 255)
                elif 0 <= val_numeric <= 100:
                    level = int(val_numeric)
                else:
                    return
                device['state']['level'] = level
                device['state']['state'] = 'on' if level > 0 else 'off'
        elif 'switch' in device_type.lower():
            if cmd_lower in ['on', 'off']:
                device['state']['state'] = cmd_lower
            elif cmd_lower == 'toggle':
                current = device['state'].get('state', 'off')
                device['state']['state'] = 'off' if current == 'on' else 'on'
        elif 'blind' in device_type.lower():
            if command.upper() in ['OPEN', 'UP']:
                device['state']['pos'] = 0
            elif command.upper() in ['CLOSE', 'DOWN']:
                device['state']['pos'] = 100

        await self.publish_device_state(sid, device)

    def eltako_level_to_mqtt_brightness(self, level: int) -> int:
        level = max(0, min(level, 100))
        return round(level * 255 / 100)

    async def publish_device_state(self, sid: str, device: Dict[str, Any]):
        device_type = device.get("data", "")
        state = device.get("state", {})
        base = f"eltako/{sid}"
        rssi = state.get("rssiPercentage", 0)
        self.mqtt_client.publish(f"{base}/rssi", rssi, retain=True)

        if "blind" in device_type.lower():
            pos = state.get("pos", 0)
            self.mqtt_client.publish(f"{base}/state", pos, retain=True)
            sync = state.get("sync", False)
            self.mqtt_client.publish(f"{base}/sync", sync, retain=True)
            rv = state.get("rv", 0)
            rt = state.get("rt", 0)
            self.mqtt_client.publish(f"{base}/rv", rv, retain=True)
            self.mqtt_client.publish(f"{base}/rt", rt, retain=True)
        elif "switch" in device_type.lower():
            st = state.get("state", "off")
            self.mqtt_client.publish(f"{base}/state", st, retain=True)
        elif "dimmer" in device_type.lower():
            st = state.get("state", "off")
            level = state.get("level", 0)
            brightness = self.eltako_level_to_mqtt_brightness(level)
            self.mqtt_client.publish(f"{base}/state", st, retain=True)
            self.mqtt_client.publish(f"{base}/brightness", brightness, retain=True)
        elif "weather" in device_type.lower():
            vals = {
                "wind": state.get("wind", 0),
                "rain": str(state.get("rain_state", False)).lower(),
                "temperature": state.get("temperature", 0),
                "illumination": state.get("illumination", 0),
                "illumination_east": state.get("s1", 0),
                "illumination_south": state.get("s2", 0),
                "illumination_west": state.get("s3", 0),
            }
            for k, v in vals.items():
                # S1/S2/S3: erst mit 1000 multiplizieren, dann runden
                if k in ("illumination_east", "illumination_south", "illumination_west"):
                    try:
                        v = float(v) * 1000
                        v = int(round(v))
                    except Exception:
                        v = 0
                # zentrale Illumination: nur runden auf int
                elif k == "illumination":
                    try:
                        v = int(round(float(v)))
                    except Exception:
                        v = 0
                self.mqtt_client.publish(f"{base}/{k}", v, retain=True)

    async def publish_discovery(self):
        logger.info("Publishing MQTT discovery")
        self.loop = asyncio.get_running_loop()
        for sid, device in self.devices.items():
            device_type = device.get("data", "")
            device_info = {
                "identifiers": [f"eltako_{sid}"],
                "name": f"Eltako {sid}",
                "model": device_type,
                "manufacturer": "Eltako",
                "via_device": "eltako_minisafe2"
            }
            if "blind" in device_type.lower():
                config = {
                    "name": f"Eltako Blind {sid}",
                    "unique_id": f"eltako_blind_{sid}",
                    "device_class": "blind",
                    "command_topic": f"eltako/{sid}/set",
                    "position_topic": f"eltako/{sid}/state",
                    "position_closed": 100,
                    "position_open": 0,
                    "payload_open": "OPEN",
                    "payload_close": "CLOSE",
                    "payload_stop": "STOP",
                    "device": device_info
                }
                topic = f"homeassistant/cover/eltako_blind_{sid}/config"
                self.mqtt_client.publish(topic, json.dumps(config), retain=True)
            elif "switch" in device_type.lower():
                config = {
                    "name": f"Eltako Switch {sid}",
                    "unique_id": f"eltako_switch_{sid}",
                    "command_topic": f"eltako/{sid}/set",
                    "state_topic": f"eltako/{sid}/state",
                    "payload_on": "on",
                    "payload_off": "off",
                    "device": device_info
                }
                topic = f"homeassistant/switch/eltako_switch_{sid}/config"
                self.mqtt_client.publish(topic, json.dumps(config), retain=True)
            elif "dimmer" in device_type.lower():
                config = {
                    "name": f"Eltako Dimmer {sid}",
                    "unique_id": f"eltako_dimmer_{sid}",
                    "command_topic": f"eltako/{sid}/set",
                    "state_topic": f"eltako/{sid}/state",
                    "brightness_command_topic": f"eltako/{sid}/set",
                    "brightness_state_topic": f"eltako/{sid}/brightness",
                    "brightness_scale": 255,
                    "payload_on": "on",
                    "payload_off": "off",
                    "device": device_info
                }
                topic = f"homeassistant/light/eltako_dimmer_{sid}/config"
                self.mqtt_client.publish(topic, json.dumps(config), retain=True)
            elif "weather" in device_type.lower():
                weather_sensors = [
                    ("wind", "Wind", "m/s", None, "sensor"),
                    ("rain", "Rain", None, None, "sensor"),
                    ("temperature", "Temperature", "°C", "temperature", "sensor"),
                    ("illumination", "Illumination", "lx", "illuminance", "sensor"),
                    ("illumination_east", "Illumination East", "lx", "illuminance", "sensor"),
                    ("illumination_south", "Illumination South", "lx", "illuminance", "sensor"),
                    ("illumination_west", "Illumination West", "lx", "illuminance", "sensor")
                ]
                for key, name, unit, devclass, platform in weather_sensors:
                    config = {
                        "name": name,
                        "unique_id": f"eltako_weather_{key}_{sid}",
                        "state_topic": f"eltako/{sid}/{key}",
                        "device": device_info
                    }
                    if unit:
                        config["unit_of_measurement"] = unit
                    if devclass:
                        config["device_class"] = devclass
                    if key == "rain":
                        config["icon"] = "mdi:weather-pouring"
                    if "wind" in key:
                        config["icon"] = "mdi:weather-windy"
                    topic = f"homeassistant/{platform}/eltako_weather_{key}_{sid}/config"
                    self.mqtt_client.publish(topic, json.dumps(config), retain=True)

    async def poll_devices(self):
        while self.running:
            try:
                devices = await self.fetch_device_states()
                if devices:
                    for device in devices:
                        sid = device.get("sid")
                        if sid:
                            self.devices[sid] = device
                            await self.publish_device_state(sid, device)
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(self.poll_interval)

    async def fetch_device_states(self) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}?XC_FNC=GetStates&XC_PASS={quote_plus(self.password)}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    if text.startswith("{XC_SUC}"):
                        json_data = text[8:]
                        return json.loads(json_data)
                    logger.error(f"Unexpected response: {text}")
                else:
                    logger.error(f"HTTP error {response.status}")
        except Exception as e:
            logger.error(f"Error fetching device states: {e}")
        return None

    async def run(self):
        logger.info("Starting Eltako2MQTT Bridge")
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        try:
            await self.setup_mqtt()
            devices = await self.fetch_device_states()
            if not devices:
                logger.error("No devices found")
                return
            for device in devices:
                sid = device.get("sid")
                if sid:
                    self.devices[sid] = device
                    logger.info(f"Found device {sid}: {device.get('data')}")
            await self.publish_discovery()
            for sid, device in self.devices.items():
                await self.publish_device_state(sid, device)
            self.running = True
            await self.poll_devices()
        except Exception as e:
            logger.error(f"Runtime error: {e}")
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            if self.session:
                await self.session.close()
            logger.info("Bridge stopped")

async def main():
    if len(sys.argv) != 2:
        print("Usage: python3 eltako2mqtt.py ")
        sys.exit(1)
    config_file = sys.argv[1]
    bridge = EltakoMiniSafe2Bridge(config_file)
    await bridge.run()

if __name__ == "__main__":
    asyncio.run(main())
