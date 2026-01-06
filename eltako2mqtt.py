#!/usr/bin/env python3

"""Eltako MiniSafe2 MQTT Bridge

Dimmerbefehle exakt: dimToX, on, off 	 keine Doppelbefehle!
"""

import asyncio
import aiohttp
import json
import logging
import signal
import sys
import yaml
import os
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
        logger.info(f"Loading configuration from: {config_file}")
        
        # Check if config file exists
        if not os.path.exists(config_file):
            logger.error(f"Config file not found: {config_file}")
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Directory contents: {os.listdir(os.path.dirname(config_file) if os.path.dirname(config_file) else '.')}")
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
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
        
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Eltako host: {self.eltako_config['host']}")
        logger.info(f"MQTT host: {self.mqtt_config['host']}:{self.mqtt_config.get('port', 1883)}")

    def load_config(self, config_file: str) -> Dict[str, Any]:
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Config file parsed successfully")
                return config
        except FileNotFoundError as e:
            logger.error(f"Failed to load config: {e}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML config: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def setup_mqtt(self):
        # Use CallbackAPIVersion.VERSION1 to preserve the 1.x callback API semantics
        # when running with paho-mqtt 2.x. This keeps existing on_connect/on_message
        # callback signatures working without modification.
        self.mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1,
            client_id=self.mqtt_config.get('client_id', 'eltako2mqtt')
        )
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
                last_time = self._last_dim_command_time.get(sid, 0)
                
                # Prevent rapid successive dimming commands
                if now - last_time < 0.5:
                    logger.debug(f"Ignoring rapid dimming command for {sid}")
                    return
                
                self._last_dim_command_time[sid] = now
                asyncio.run_coroutine_threadsafe(
                    self.handle_mqtt_command(sid, payload),
                    self.loop
                )
            else:
                logger.error("No event loop set for scheduling command")

    def on_mqtt_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker: {rc}")

    async def handle_mqtt_command(self, sid: str, command: str):
        try:
            device = self.devices.get(sid)
            if not device:
                logger.warning(f"Device {sid} not found")
                return

            # Construct the command
            dim_value = None
            if command == "on":
                dim_value = 255
            elif command == "off":
                dim_value = 0
            elif command.startswith("dimTo"):
                try:
                    dim_value = int(command[5:])
                except (ValueError, IndexError):
                    logger.error(f"Invalid dim command: {command}")
                    return

            if dim_value is not None:
                await self.send_command(sid, dim_value)
        except Exception as e:
            logger.error(f"Error handling MQTT command: {e}")

    async def send_command(self, sid: str, value: int):
        """Send a command to the Eltako device"""
        try:
            # URL encode the password
            encoded_pwd = quote_plus(self.password)
            url = f"{self.base_url}?pwd={encoded_pwd}&sid={sid}&command=dimToX&value={value}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    logger.info(f"Command sent to device {sid}: dimToX({value})")
                else:
                    logger.error(f"Failed to send command to device {sid}: {response.status}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout sending command to device {sid}")
        except Exception as e:
            logger.error(f"Error sending command to device {sid}: {e}")

    async def fetch_devices(self):
        """Fetch device list from Eltako device"""
        try:
            encoded_pwd = quote_plus(self.password)
            url = f"http://{self.eltako_config['host']}/list?pwd={encoded_pwd}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    self.devices = self.parse_device_list(content)
                    logger.info(f"Fetched {len(self.devices)} devices from Eltako")
                    return True
                else:
                    logger.error(f"Failed to fetch devices: HTTP {response.status}")
                    return False
        except asyncio.TimeoutError:
            logger.error("Timeout fetching device list from Eltako")
            return False
        except Exception as e:
            logger.error(f"Error fetching device list: {e}")
            return False

    def parse_device_list(self, html_content: str) -> Dict[str, Any]:
        """Parse device list from Eltako HTML response"""
        devices = {}
        lines = html_content.split('\n')
        
        for line in lines:
            if '<tr>' in line:
                # Parse table row for device info
                parts = line.split('|')
                if len(parts) >= 3:
                    try:
                        sid = parts[0].strip()
                        name = parts[1].strip()
                        # Device found
                        devices[sid] = {
                            'name': name,
                            'sid': sid
                        }
                    except (IndexError, ValueError):
                        continue
        
        return devices

    async def publish_discovery(self):
        """Publish Home Assistant discovery messages"""
        try:
            for sid, device in self.devices.items():
                # Create discovery message for Home Assistant
                discovery_topic = f"homeassistant/light/{sid}/config"
                discovery_payload = {
                    "name": device.get('name', f"Eltako {sid}"),
                    "unique_id": f"eltako_{sid}",
                    "command_topic": f"eltako/{sid}/set",
                    "state_topic": f"eltako/{sid}/state",
                    "brightness": True,
                    "schema": "json",
                    "device": {
                        "identifiers": [f"eltako_{sid}"],
                        "name": f"Eltako {sid}"
                    }
                }
                
                self.mqtt_client.publish(
                    discovery_topic,
                    json.dumps(discovery_payload),
                    retain=True
                )
                logger.debug(f"Published discovery for device {sid}")
        except Exception as e:
            logger.error(f"Error publishing discovery: {e}")

    async def poll_devices(self):
        """Periodically poll device status from Eltako"""
        while self.running:
            try:
                await self.fetch_devices()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(5)

    async def run(self):
        """Main run loop"""
        self.running = True
        self.loop = asyncio.get_event_loop()
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession()
        
        try:
            # Setup MQTT
            await self.setup_mqtt()
            
            # Initial device fetch
            await self.fetch_devices()
            
            # Start polling
            polling_task = asyncio.create_task(self.poll_devices())
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
            
            polling_task.cancel()
        except Exception as e:
            logger.error(f"Error in run: {e}")
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            if self.session:
                await self.session.close()
            self.running = False

async def main():
    """Main entry point"""
    # Support both ways of being called
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "/config/eltako2mqtt/options.yaml"
    
    logger.info(f"Using config file: {config_file}")
    
    try:
        bridge = EltakoMiniSafe2Bridge(config_file)
        await bridge.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
