"""Release contracts tested against real installed dependencies."""

import asyncio
from contextlib import nullcontext
import importlib.metadata
import inspect
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

import paho.mqtt.client as mqtt
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eltako2mqtt import EltakoMiniSafe2Bridge
from state_feedback import StateFeedbackBridge
from bridge_base import EltakoMiniSafe2Bridge as BridgeBase
from tools.check_links import check_documents


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
        self.assertNotIn("py3-yaml", dockerfile)
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

    def test_legacy_behavior_cannot_be_instantiated_or_accidentally_reused(self):
        self.assertTrue(inspect.isabstract(BridgeBase))
        self.assertFalse(inspect.isabstract(StateFeedbackBridge))
        self.assertEqual(BridgeBase.__abstractmethods__, {
            "handle_device_command", "poll_devices", "fetch_device_states",
            "_is_recently_commanded",
        })
        self.assertFalse(hasattr(BridgeBase, "update_device_state_immediate"))
        self.assertFalse(hasattr(BridgeBase, "eltako_level_to_mqtt_brightness"))
        with self.assertRaises(TypeError):
            BridgeBase("unused-config.yaml")

    def test_manifest_requests_only_used_services(self):
        config = yaml.safe_load((ROOT / "config.yaml").read_text())
        for key in ("hassio_api", "hassio_role", "map", "ports"):
            self.assertNotIn(key, config)
        self.assertEqual(config["services"], ["mqtt:need"])

    def test_architectures_and_base_migration_are_deliberately_unchanged(self):
        config = yaml.safe_load((ROOT / "config.yaml").read_text())
        build = yaml.safe_load((ROOT / "build.yaml").read_text())["build_from"]
        expected = {"aarch64", "amd64", "armhf", "armv7", "i386"}
        self.assertEqual(set(config["arch"]), expected)
        self.assertEqual(set(build), expected)
        for arch, image in build.items():
            self.assertEqual(image, f"ghcr.io/home-assistant/{arch}-base:3.18")
        # PyYAML treats the workflow key 'on' as a YAML-1.1 boolean, but jobs
        # are unaffected. Only inspect the relevant job structure here.
        workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
        matrix = workflow["jobs"]["container"]["strategy"]["matrix"]["include"]
        self.assertEqual({row["arch"] for row in matrix}, expected)

    def test_google_verification_is_preserved_byte_for_byte(self):
        self.assertEqual(
            (ROOT / "google89c77ea745b77da5.html").read_bytes(),
            b"google-site-verification: google89c77ea745b77da5.html",
        )

    def test_production_initialization_uses_shared_config_defaults_and_overrides(self):
        for extra, expected_poll, expected_timeout in (
            ({}, 30, 120),
            ({"poll_interval": 60, "command_feedback_timeout": 300}, 60, 300),
        ):
            config = {
                "eltako": {"host": "minisafe", "password": "fixture", **extra},
                "mqtt": {"host": "broker"},
            }
            with patch.object(BridgeBase, "load_config", return_value=config), \
                    patch("bridge_base.signal.signal"), \
                    patch("bridge_base.logging.basicConfig"):
                bridge = StateFeedbackBridge("unused-config.yaml")
            self.assertEqual(bridge.poll_interval, expected_poll)
            self.assertEqual(bridge._command_timeout, expected_timeout)
            self.assertNotIn("_recently_commanded_device", vars(bridge))

    def test_launcher_serialization_preserves_credentials_and_optional_defaults(self):
        script = (ROOT / "run.sh").read_text()
        code = script.split("<<'PY'\n", 1)[1].split("\nPY", 1)[0]
        self.assertIn("umask 077", script)
        fixture = 'quotes" slash\\ newline\n hash# colon: dollar$ amp& unicodeä'
        for feedback in ({}, {"command_feedback_timeout": 360}):
            options = {
                "eltako": {"host": "minisafe", "password": fixture, **feedback},
                "mqtt": {"host": "broker", "username": "user", "password": fixture},
            }
            source = io.StringIO(json.dumps(options))
            target = io.StringIO()

            def open_fixture(path, mode="r", **kwargs):
                self.assertEqual(path, "/data/options.json" if mode == "r" else "/tmp/eltako2mqtt.yaml")
                return nullcontext(source if mode == "r" else target)

            # Exercise the exact launcher snippet without persisting credential
            # fixtures to disk or spawning a process with them in its arguments.
            with patch("builtins.open", side_effect=open_fixture):
                exec(compile(code, "run.sh:configuration", "exec"), {})
            config = yaml.safe_load(target.getvalue())
            self.assertEqual(config["eltako"]["password"], fixture)
            self.assertEqual(config["mqtt"]["password"], fixture)
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
        checked, problems = check_documents(ROOT)
        self.assertGreater(checked, 0)
        self.assertEqual(problems, [])
