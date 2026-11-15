"""Regression tests for rain discovery and legacy discovery cleanup."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from bridge_base import EltakoMiniSafe2Bridge


class RainDiscoveryTests(unittest.IsolatedAsyncioTestCase):
    def make_bridge(self):
        return SimpleNamespace(
            devices={"weather1": {"data": "weather", "state": {}}},
            mqtt_client=Mock(),
            is_switch_device=lambda device_type: False,
            discovery_count=0,
        )

    async def test_rain_is_moisture_binary_sensor_and_legacy_is_removed_first(self):
        bridge = self.make_bridge()
        await EltakoMiniSafe2Bridge.publish_discovery(bridge)
        calls = bridge.mqtt_client.publish.call_args_list
        legacy = "homeassistant/sensor/eltako_weather_rain_weather1/config"
        topic = "homeassistant/binary_sensor/eltako_weather_rain_weather1/config"
        cleanup = next(i for i, c in enumerate(calls) if c.args[0] == legacy)
        creation = next(i for i, c in enumerate(calls) if c.args[0] == topic)
        self.assertLess(cleanup, creation)
        self.assertEqual(calls[cleanup].args[1], "")
        self.assertTrue(calls[cleanup].kwargs["retain"])
        config = json.loads(calls[creation].args[1])
        self.assertEqual(config["device_class"], "moisture")
        self.assertEqual(config["payload_on"], "true")
        self.assertEqual(config["payload_off"], "false")
        self.assertEqual(config["state_topic"], "eltako/weather1/rain")
        self.assertEqual(config["unique_id"], "eltako_weather_rain_weather1")
        self.assertNotIn("unit_of_measurement", config)
        self.assertTrue(calls[creation].kwargs["retain"])
        self.assertEqual(bridge.discovery_count, 7)
        configs = {c.args[0]: json.loads(c.args[1]) for c in calls if c.args[1]}
        self.assertEqual(len(configs), 7)
        temperature = configs["homeassistant/sensor/eltako_weather_temperature_weather1/config"]
        self.assertEqual(temperature["device_class"], "temperature")
        self.assertEqual(temperature["unit_of_measurement"], "°C")

    async def test_discovery_can_be_repeated(self):
        bridge = self.make_bridge()
        await EltakoMiniSafe2Bridge.publish_discovery(bridge)
        first = list(bridge.mqtt_client.publish.call_args_list)
        bridge.mqtt_client.reset_mock()
        await EltakoMiniSafe2Bridge.publish_discovery(bridge)
        self.assertEqual(bridge.mqtt_client.publish.call_args_list, first)
        self.assertEqual(bridge.discovery_count, 7)

    async def test_rain_state_payloads_stay_compatible(self):
        bridge = self.make_bridge()
        for wet, expected in ((True, "true"), (False, "false")):
            with self.subTest(wet=wet):
                bridge.mqtt_client.reset_mock()
                device = {"data": "weather", "state": {"rain_state": wet}}
                await EltakoMiniSafe2Bridge.publish_device_state(bridge, "weather1", device)
                bridge.mqtt_client.publish.assert_any_call(
                    "eltako/weather1/rain", expected, retain=True
                )


if __name__ == "__main__":
    unittest.main()
