"""
#!/usr/bin/env python3

"""

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
