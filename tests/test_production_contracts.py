"""Release contracts tested against real installed dependencies."""

import asyncio
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import paho.mqtt.client as mqtt
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eltako2mqtt import EltakoMiniSafe2Bridge
from state_feedback import StateFeedbackBridge


class ProductionContracts(unittest.TestCase):
    def test_entry_point_selects_production_feedback(self):
        self.assertIs(EltakoMiniSafe2Bridge, StateFeedbackBridge)
        completed = subprocess.run(
            [sys.executable, str(ROOT / "eltako2mqtt.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("Usage: python3 eltako2mqtt.py", completed.stdout)

    def test_docker_sources_exist_and_dependencies_have_one_source(self):
        dockerfile = (ROOT / "Dockerfile").read_text()
        for source in re.findall(r"^COPY (\S+) ", dockerfile, re.MULTILINE):
            self.assertTrue((ROOT / source).is_file(), source)
        self.assertIn("pip3 install --no-cache-dir -r /requirements.txt", dockerfile)
        self.assertNotIn("paho-mqtt==", dockerfile)
        self.assertNotIn("experimental", dockerfile.lower())
        self.assertIn("exec python3 /eltako2mqtt.py", (ROOT / "run.sh").read_text())

    def test_release_identity_versions_and_dependencies(self):
        config = yaml.safe_load((ROOT / "config.yaml").read_text())
        self.assertEqual(config["version"], "1.3.0")
        self.assertEqual(config["slug"], "eltako2mqtt")
        self.assertEqual(config["name"], "Eltako2MQTT")
        self.assertEqual(config["options"]["mqtt"]["client_id"], "eltako2mqtt")
        self.assertEqual(config["options"]["eltako"]["poll_interval"], 30)
        self.assertEqual(config["options"]["eltako"]["command_feedback_timeout"], 120)
        self.assertIn('io.hass.version="1.3.0"', (ROOT / "Dockerfile").read_text())
        for requirement in (ROOT / "requirements.txt").read_text().splitlines():
            name, version = requirement.split("==")
            self.assertEqual(importlib.metadata.version(name), version)

    def test_launcher_serialization_preserves_credentials_and_optional_defaults(self):
        script = (ROOT / "run.sh").read_text()
        code = script.split("<<'PY'\n", 1)[1].split("\nPY", 1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            options_path = Path(tmp) / "options.json"
            output_path = Path(tmp) / "bridge.yaml"
            code = code.replace("/data/options.json", str(options_path))
            code = code.replace("/tmp/eltako2mqtt.yaml", str(output_path))
            secret = 'quotes" slash\\ newline\n hash# colon: dollar$ amp& unicodeä'
            for feedback in ({}, {"command_feedback_timeout": 360}):
                options = {
                    "eltako": {"host": "minisafe", "password": secret, **feedback},
                    "mqtt": {"host": "broker", "username": "user", "password": secret},
                }
                options_path.write_text(json.dumps(options))
                subprocess.run([sys.executable, "-c", code], check=True)
                config = yaml.safe_load(output_path.read_text())
                self.assertEqual(config["eltako"]["password"], secret)
                self.assertEqual(config["mqtt"]["password"], secret)
                self.assertEqual(config["eltako"]["command_feedback_timeout"],
                                 feedback.get("command_feedback_timeout", 120))
                self.assertEqual(config["eltako"]["poll_interval"], 30)
                self.assertEqual(config["mqtt"]["port"], 1883)
                self.assertEqual(config["mqtt"]["client_id"], "eltako2mqtt")

    def test_real_paho_version2_callbacks_without_network(self):
        bridge = StateFeedbackBridge.__new__(StateFeedbackBridge)
        bridge.mqtt_config = {"host": "broker", "client_id": "contract-test"}
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        with patch("bridge_base.mqtt.Client", return_value=client), \
                patch.object(client, "connect") as connect, \
                patch.object(client, "loop_start"):
            asyncio.run(bridge.setup_mqtt())
        connect.assert_called_once_with("broker", 1883, 60)
        client.subscribe = Mock()
        bridge.on_mqtt_connect(client, None, mqtt.ConnectFlags(False),
                               mqtt.ReasonCode(mqtt.PacketTypes.CONNACK, "Success"), None)
        self.assertTrue(bridge.mqtt_connected)
        self.assertEqual(client.subscribe.call_count, 2)
        bridge.on_mqtt_disconnect(client, None, mqtt.DisconnectFlags(False),
                                  mqtt.ReasonCode(mqtt.PacketTypes.DISCONNECT, "Normal disconnection"), None)
        self.assertFalse(bridge.mqtt_connected)

    def test_documentation_relative_links_resolve(self):
        documents = [ROOT / "README.md", ROOT / "CHANGELOG.md", *sorted((ROOT / "docs").glob("*.md"))]
        for document in documents:
            for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", document.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                path = target.split("#", 1)[0]
                self.assertTrue((document.parent / path).exists(), f"{document.name}: {target}")
