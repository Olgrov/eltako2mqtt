import asyncio
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import paho.mqtt.client
except ImportError:
    paho = types.ModuleType('paho')
    mqtt_pkg = types.ModuleType('paho.mqtt')
    mqtt = types.ModuleType('paho.mqtt.client')
    for name in ('Client', 'MQTTMessage', 'ConnectFlags', 'ReasonCode', 'DisconnectFlags'):
        setattr(mqtt, name, object)
    mqtt.CallbackAPIVersion = types.SimpleNamespace(VERSION2=2)
    sys.modules.update({'paho': paho, 'paho.mqtt': mqtt_pkg, 'paho.mqtt.client': mqtt})

spec = importlib.util.spec_from_file_location('experimental', Path(__file__).parents[1] / 'eltako2mqtt_experimental.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MQTT:
    def __init__(self):
        self.messages = []

    def publish(self, topic, payload, retain=False):
        self.messages.append((topic, payload, retain))


def blind(pos):
    return {'sid': '01', 'data': 'eltako_blind', 'adr': 'address', 'state': {'pos': pos}}


class Tests(unittest.IsolatedAsyncioTestCase):
    def bridge(self):
        b = module.ExperimentalBridge.__new__(module.ExperimentalBridge)
        b.pending_commands = {}
        b._last_command_time = {}
        b._recently_commanded_device = None
        b._command_timeout = 90
        b.poll_interval = 30
        b._last_poll_started = None
        b.minisafe_lock = asyncio.Lock()
        b.devices = {}
        b.mqtt_client = MQTT()
        b.base_url = 'http://minisafe/command'
        b.password = 'test-placeholder'
        return b

    async def test_slider_close_publishes_closing_without_mutation(self):
        b = self.bridge()
        d = blind(0)
        b._track_pending('01', '0', d)  # HA: 0 = closed, MiniSafe status: 100 = closed
        await b._publish_command_feedback('01')
        self.assertEqual(d['state']['pos'], 0)
        self.assertEqual(b.pending_commands['01']['expected']['pos'], 100)
        self.assertIn(('eltako/01/movement', 'closing', False), b.mqtt_client.messages)

    def test_slider_open_maps_to_raw_open_endpoint(self):
        b = self.bridge()
        b._track_pending('01', '100', blind(100))
        self.assertEqual(b.pending_commands['01']['expected']['pos'], 0)
        self.assertEqual(b.pending_commands['01']['movement'], 'opening')

    def test_slider_intermediate_directions(self):
        for ha_target, expected, movement in [('25', 75, 'closing'), ('75', 25, 'opening'), ('50', 50, 'stopped')]:
            with self.subTest(target=ha_target):
                b = self.bridge()
                b._track_pending('01', ha_target, blind(50))
                self.assertEqual(b.pending_commands['01']['expected']['pos'], expected)
                self.assertEqual(b.pending_commands['01']['movement'], movement)

    def test_open_close_stop_commands(self):
        for cmd, movement in [('open', 'opening'), ('up', 'opening'), ('close', 'closing'), ('down', 'closing'), ('stop', 'stopped')]:
            with self.subTest(cmd=cmd):
                b = self.bridge()
                b._track_pending('01', cmd, blind(50))
                self.assertEqual(b.pending_commands['01']['movement'], movement)

    async def test_close_confirmed_at_next_poll_not_after_timeout(self):
        b = self.bridge()
        b._track_pending('01', '0', blind(0))
        b.pending_commands['01']['timestamp'] -= 30
        actual = blind(100)
        b._reconcile_pending('01', actual)
        b.devices['01'] = actual
        await b.publish_device_state('01', actual)
        self.assertNotIn('01', b.pending_commands)
        self.assertIn(('eltako/01/state', 100, True), b.mqtt_client.messages)
        self.assertIn(('eltako/01/movement', 'closed', False), b.mqtt_client.messages)

    async def test_pending_does_not_mask_unchanged_poll_for_90_seconds(self):
        b = self.bridge()
        b._track_pending('01', 'close', blind(0))
        b.pending_commands['01']['timestamp'] -= 30
        actual = blind(0)
        b._reconcile_pending('01', actual)
        await b.publish_device_state('01', actual)
        self.assertIn('01', b.pending_commands)
        self.assertIn(('eltako/01/movement', 'open', False), b.mqtt_client.messages)
        self.assertNotIn(('eltako/01/movement', 'closing', False), b.mqtt_client.messages)

    async def test_polled_progress_and_stationary_partial_position(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        b._track_pending('01', 'close', blind(0))
        b.pending_commands['01']['timestamp'] -= 30
        b._reconcile_pending('01', blind(45))
        await b.publish_device_state('01', blind(45))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'closing')
        b.devices['01'] = blind(45)
        b._reconcile_pending('01', blind(45))
        await b.publish_device_state('01', blind(45))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'stopped')

    async def test_external_polled_movement(self):
        b = self.bridge()
        b.devices['01'] = blind(80)
        b._reconcile_pending('01', blind(30))
        await b.publish_device_state('01', blind(30))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'opening')

    async def test_string_position_does_not_abort_poll_publication(self):
        b = self.bridge()
        await b.publish_device_state('01', blind('100'))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'closed')

    async def test_invalid_position_does_not_fabricate_endpoint(self):
        b = self.bridge()
        await b.publish_device_state('01', blind(None))
        topics = [message[0] for message in b.mqtt_client.messages]
        self.assertNotIn('eltako/01/state', topics)
        self.assertNotIn('eltako/01/movement', topics)

    def test_numeric_match_rejects_nan(self):
        b = self.bridge()
        self.assertFalse(b._pending_matches({'expected': {'pos': 100}}, blind('nan')))

    async def test_discovery_disables_cover_position_prediction_only(self):
        b = self.bridge()
        b.devices = {'01': blind(0), '11': {'data': 'eltako_switch'}, '13': {'data': 'eltako_dimmer'}}
        await b.publish_discovery()
        configs = {topic: json.loads(payload) for topic, payload, _ in b.mqtt_client.messages if topic.endswith('/config')}
        c = configs['homeassistant/cover/eltako_blind_01/config']
        self.assertFalse(c['optimistic'])
        self.assertEqual(c['position_closed'], 100)
        self.assertEqual(c['position_open'], 0)
        self.assertEqual(c['set_position_template'], '{{ position }}')
        self.assertTrue(configs['homeassistant/light/eltako_dimmer_13/config']['optimistic'])
        self.assertTrue(configs['homeassistant/switch/eltako_switch_11/config']['optimistic'])

    def test_polled_switch_state_confirms_command(self):
        b = self.bridge()
        b._track_pending('11', 'on', {'data': 'eltako_switch', 'state': {'state': 'off'}})
        b._reconcile_pending('11', {'data': 'eltako_switch', 'state': {'state': 'on'}})
        self.assertNotIn('11', b.pending_commands)

    def test_dimmer_expected_value(self):
        b = self.bridge()
        b._track_pending('13', '128', {'data': 'eltako_dimmer', 'state': {'state': 'off', 'level': 0}})
        self.assertEqual(b.pending_commands['13']['expected'], {'state': 'on', 'level': 50})

    def test_timeout_only_removes_diagnostic_pending(self):
        b = self.bridge()
        b._track_pending('01', 'close', blind(0))
        b.pending_commands['01']['timestamp'] -= 100
        with self.assertLogs(module.logger, level='WARNING'):
            b._reconcile_pending('01', blind(0))
        self.assertNotIn('01', b.pending_commands)

    async def test_external_endpoint_is_terminal_not_still_moving(self):
        b = self.bridge()
        b.devices['01'] = blind(20)
        b._reconcile_pending('01', blind(100))
        await b.publish_device_state('01', blind(100))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'closed')

    async def test_recent_old_snapshot_has_only_short_grace(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        b._track_pending('01', 'close', blind(0))
        b._reconcile_pending('01', blind(0))
        await b.publish_device_state('01', blind(0))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'closing')
        b.pending_commands['01']['timestamp'] -= 3
        b._reconcile_pending('01', blind(0))
        await b.publish_device_state('01', blind(0))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'open')

    async def test_serialized_requests_and_no_command_triggered_poll(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        active = 0
        maximum = 0
        requests = []

        class Response:
            status = 200
            def __init__(self, url):
                self.url = url
            async def __aenter__(self):
                nonlocal active, maximum
                if not b.minisafe_lock.locked():
                    raise AssertionError('request without lock')
                active += 1
                maximum = max(maximum, active)
                requests.append(self.url)
                await asyncio.sleep(0)
                return self
            async def __aexit__(self, *args):
                nonlocal active
                active -= 1
            async def text(self):
                return '{XC_SUC}' + (json.dumps([blind(0)]) if 'GetStates' in self.url else '')

        b.session = types.SimpleNamespace(get=Response)
        await asyncio.gather(b.fetch_device_states(), b.handle_device_command('01', 'close'))
        self.assertEqual(maximum, 1)
        self.assertEqual(sum('GetStates' in url for url in requests), 1)
        self.assertEqual(sum('SendSC' in url for url in requests), 1)
        self.assertEqual(b.devices['01']['state']['pos'], 0)
        self.assertIn(('eltako/01/movement', 'closing', False), b.mqtt_client.messages)

    async def test_startup_poll_spacing_does_not_block_commands(self):
        b = self.bridge()
        b._last_poll_started = module.time.monotonic()
        request_times = []
        slept = []

        class Response:
            status = 200
            async def __aenter__(self):
                request_times.append(module.time.monotonic())
                return self
            async def __aexit__(self, *args):
                pass
            async def text(self):
                return '{XC_SUC}[]'

        async def advance(delay):
            self.assertFalse(b.minisafe_lock.locked())
            slept.append(delay)
            b._last_poll_started -= delay + 0.01

        b.session = types.SimpleNamespace(get=lambda url: Response())
        with patch.object(module.asyncio, 'sleep', advance):
            await b.fetch_device_states()
        self.assertEqual(len(slept), 1)
        self.assertGreater(slept[0], 29)
        self.assertEqual(len(request_times), 1)


if __name__ == '__main__':
    unittest.main()
