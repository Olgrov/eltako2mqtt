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
        b._command_timeout = 120
        b._cover_movements = {}
        b._pending_timeout_tasks = {}
        b._invalid_brightness = set()
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

    async def test_pending_retains_direction_but_publishes_real_position(self):
        b = self.bridge()
        b._track_pending('01', 'close', blind(0))
        b.pending_commands['01']['timestamp'] -= 30
        actual = blind(0)
        b._reconcile_pending('01', actual)
        await b.publish_device_state('01', actual)
        self.assertIn('01', b.pending_commands)
        self.assertIn(('eltako/01/state', 0, True), b.mqtt_client.messages)
        self.assertIn(('eltako/01/movement', 'closing', False), b.mqtt_client.messages)

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
        self.assertEqual(b.mqtt_client.messages[-1][1], 'closing')

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

    def test_timeout_clears_pending_without_touching_polled_position(self):
        b = self.bridge()
        b._track_pending('01', 'close', blind(0))
        b.pending_commands['01']['timestamp'] -= 121
        with self.assertLogs(module.logger, level='WARNING'):
            b._reconcile_pending('01', blind(0))
        self.assertNotIn('01', b.pending_commands)

    async def test_external_endpoint_is_terminal_not_still_moving(self):
        b = self.bridge()
        b.devices['01'] = blind(20)
        b._reconcile_pending('01', blind(100))
        await b.publish_device_state('01', blind(100))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'closed')

    async def test_recent_old_snapshot_does_not_cancel_movement_after_two_seconds(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        b._track_pending('01', 'close', blind(0))
        b._reconcile_pending('01', blind(0))
        await b.publish_device_state('01', blind(0))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'closing')
        b.pending_commands['01']['timestamp'] -= 3
        b._reconcile_pending('01', blind(0))
        await b.publish_device_state('01', blind(0))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'closing')

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


    async def test_log_replay_delayed_endpoint_keeps_closing_for_81_seconds(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        with patch.object(module.time, 'monotonic', return_value=1000):
            b._track_pending('01', '0', blind(0))
        for age, raw, movement in [(21.1, 0, 'closing'), (51.1, 0, 'closing'), (81.2, 100, 'closed')]:
            with patch.object(module.time, 'monotonic', return_value=1000 + age):
                actual = blind(raw)
                b._reconcile_pending('01', actual)
                b.devices['01'] = actual
                await b.publish_device_state('01', actual)
            self.assertEqual(b.mqtt_client.messages[-1][1], movement)
            self.assertEqual(actual['state']['pos'], raw)
        self.assertNotIn('01', b.pending_commands)

    async def test_log_replay_reversal_keeps_latest_direction(self):
        b = self.bridge()
        b.devices['01'] = blind(26)
        b._track_pending('01', 'open', blind(26))
        b.pending_commands['01']['timestamp'] -= 20
        b._reconcile_pending('01', blind(47))
        await b.publish_device_state('01', blind(47))
        self.assertEqual(b.mqtt_client.messages[-1][1], 'opening')
        self.assertIn('01', b.pending_commands)
        self.assertIn(('eltako/01/state', 47, True), b.mqtt_client.messages)

    async def test_timeout_releases_motion_at_current_real_position(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        b._track_pending('01', 'close', blind(0))
        b.pending_commands['01']['timestamp'] -= 121
        with self.assertLogs(module.logger, level='WARNING') as logs:
            b._reconcile_pending('01', blind(47))
        await b.publish_device_state('01', blind(47))
        self.assertNotIn('01', b.pending_commands)
        self.assertEqual(b.mqtt_client.messages[-1][1], 'stopped')
        self.assertIn('no command retry', logs.output[0])

    async def test_watchdog_expires_even_without_successful_polls(self):
        b = self.bridge()
        b._command_timeout = 0
        b.devices['01'] = blind(0)
        b._track_pending('01', 'close', blind(0))
        with self.assertLogs(module.logger, level='WARNING'):
            b._schedule_pending_timeout('01')
            await b._pending_timeout_tasks['01']
        self.assertNotIn('01', b.pending_commands)
        self.assertIn(('eltako/01/movement', 'open', False), b.mqtt_client.messages)
        self.assertFalse(b._pending_timeout_tasks)

    async def test_old_watchdog_does_not_expire_replacement(self):
        b = self.bridge()
        b._track_pending('01', 'close', blind(0))
        old = b.pending_commands['01']
        b._track_pending('01', 'open', blind(100))
        b._command_timeout = 0
        await b._pending_watchdog('01', old)
        self.assertEqual(b.pending_commands['01']['command'], 'open')
        self.assertFalse(b.mqtt_client.messages)

    async def test_stop_sample_is_not_logged_as_motor_confirmation(self):
        b = self.bridge()
        b._track_pending('01', 'stop', blind(26))
        self.assertFalse(b._pending_matches(b.pending_commands['01'], blind(47)))
        with self.assertLogs(module.logger, level='DEBUG') as logs:
            b._reconcile_pending('01', blind(47))
        self.assertNotIn('01', b.pending_commands)
        self.assertEqual(b._cover_movements['01'], 'stopped')
        self.assertTrue(any('motor stop not independently verified' in msg for msg in logs.output))
        self.assertFalse(any('Command confirmed' in msg for msg in logs.output))

    async def test_tracking_multiple_devices_and_supersession(self):
        b = self.bridge()
        b._track_pending('01', 'close', blind(0))
        b._track_pending('02', 'open', blind(100))
        self.assertTrue(b._is_recently_commanded('01'))
        self.assertTrue(b._is_recently_commanded('02'))
        b._track_pending('01', 'stop', blind(0))
        self.assertEqual(b.pending_commands['01']['command'], 'stop')
        self.assertIn('02', b.pending_commands)

    async def test_invalid_dimmer_level_never_publishes_fabricated_zero(self):
        for level in [None, 'nan', float('inf'), True, -1, 101, 'invalid']:
            with self.subTest(level=level):
                b = self.bridge()
                d = {'data': 'eltako_dimmer', 'state': {'state': 'on', 'level': level}}
                with self.assertLogs(module.logger, level='WARNING') as logs:
                    await b.publish_device_state('13', d)
                self.assertIn('13', logs.output[0])
                self.assertEqual(b.mqtt_client.messages, [('eltako/13/rssi', 0, True), ('eltako/13/state', 'on', True)])
                with self.assertNoLogs(module.logger, level='WARNING'):
                    await b.publish_device_state('13', d)

    async def test_valid_brightness_recovers_and_preserves_rssi(self):
        b = self.bridge()
        b._invalid_brightness.add('13')
        await b.publish_device_state('13', {'data': 'eltako_dimmer', 'state': {'state': 'on', 'level': '45.5', 'rssiPercentage': 84}})
        self.assertNotIn('13', b._invalid_brightness)
        self.assertIn(('eltako/13/brightness', 116, True), b.mqtt_client.messages)
        self.assertIn(('eltako/13/rssi', 84, True), b.mqtt_client.messages)

    async def test_off_confirmation_does_not_require_zero_level(self):
        b = self.bridge()
        d = {'data': 'eltako_dimmer', 'state': {'state': 'on', 'level': 45}}
        for command in ['off', '0']:
            b._track_pending('13', command, d)
            self.assertTrue(b._pending_matches(b.pending_commands['13'], {'state': {'state': 'off', 'level': None}}))

    async def test_payload_validation_rejects_wrong_container_and_bad_entries(self):
        with self.assertLogs(module.logger, level='ERROR'):
            self.assertIsNone(module.ExperimentalBridge._validate_device_states({'sid': '01'}))
        good = blind(0)
        with self.assertLogs(module.logger, level='WARNING'):
            result = module.ExperimentalBridge._validate_device_states([None, 1, {}, {'sid': '02', 'state': None}, good])
        self.assertEqual(result, [good])

    async def test_command_success_sends_no_extra_getstates(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        calls = []
        class Response:
            status = 200
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def text(self): return '{XC_SUC}'
        class Session:
            def get(self, url):
                calls.append(url)
                return Response()
        b.session = Session()
        await b.handle_device_command('01', ' close ')
        self.assertEqual(len(calls), 1)
        self.assertIn('XC_FNC=SendSC', calls[0])
        self.assertEqual(b.pending_commands['01']['command'], 'close')
        b._clear_pending('01')

    async def test_watchdog_cancelled_when_target_confirmed(self):
        b = self.bridge()
        b._track_pending('01', 'close', blind(0))
        b._schedule_pending_timeout('01')
        task = b._pending_timeout_tasks['01']
        b._reconcile_pending('01', blind(100))
        await asyncio.gather(task, return_exceptions=True)
        self.assertFalse(b._pending_timeout_tasks)

    async def test_failed_command_does_not_create_motion_or_pending(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        class Response:
            status = 500
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def text(self): return 'failed'
        b.session = types.SimpleNamespace(get=lambda url: Response())
        with self.assertLogs(module.logger, level='ERROR'):
            await b.handle_device_command('01', 'close')
        self.assertFalse(b.pending_commands)
        self.assertFalse(b._pending_timeout_tasks)
        self.assertFalse(b.mqtt_client.messages)

    async def test_pending_confirmed_without_valid_brightness_when_off(self):
        b = self.bridge()
        b._track_pending('13', 'off', {'data': 'eltako_dimmer', 'state': {'state': 'on'}})
        b._reconcile_pending('13', {'data': 'eltako_dimmer', 'state': {'state': 'off', 'level': None}})
        self.assertNotIn('13', b.pending_commands)

    async def test_command_waits_for_active_http_poll(self):
        b = self.bridge()
        b.devices['01'] = blind(0)
        entered = asyncio.Event()
        release = asyncio.Event()
        active = 0
        maximum = 0
        calls = []
        class Response:
            status = 200
            def __init__(self, url): self.url = url
            async def __aenter__(self):
                nonlocal active, maximum
                active += 1
                maximum = max(maximum, active)
                return self
            async def __aexit__(self, *args):
                nonlocal active
                active -= 1
            async def text(self):
                if 'GetStates' in self.url:
                    entered.set()
                    await release.wait()
                    return '{XC_SUC}' + json.dumps([blind(0)])
                return '{XC_SUC}'
        class Session:
            def get(self, url):
                calls.append(url)
                return Response(url)
        b.session = Session()
        poll = asyncio.create_task(b.fetch_device_states())
        await entered.wait()
        cmd = asyncio.create_task(b.handle_device_command('01', 'close'))
        await asyncio.sleep(0)
        self.assertEqual(len(calls), 1)
        release.set()
        await asyncio.gather(poll, cmd)
        self.assertEqual(maximum, 1)
        self.assertEqual(len(calls), 2)
        b._clear_pending('01')

    async def test_watchdog_cancelled_on_replacement(self):
        b = self.bridge()
        b._track_pending('01', 'close', blind(0))
        b._schedule_pending_timeout('01')
        old_task = b._pending_timeout_tasks['01']
        b._track_pending('01', 'open', blind(100))
        await asyncio.gather(old_task, return_exceptions=True)
        self.assertTrue(old_task.cancelled())
        self.assertEqual(b.pending_commands['01']['command'], 'open')

    async def test_invalid_numeric_feedback_never_confirms_command(self):
        b = self.bridge()
        for value in [True, -1, 101, 'nan', None]:
            self.assertFalse(b._pending_matches({'expected': {'pos': 0}}, blind(value)))


if __name__ == '__main__':
    unittest.main()
