import importlib.util
import sys
import types
import unittest
from pathlib import Path

paho = types.ModuleType('paho'); mqtt_pkg = types.ModuleType('paho.mqtt'); mqtt = types.ModuleType('paho.mqtt.client')
mqtt.Client = mqtt.MQTTMessage = mqtt.ConnectFlags = mqtt.ReasonCode = mqtt.DisconnectFlags = object
mqtt.CallbackAPIVersion = types.SimpleNamespace(VERSION2=2)
sys.modules.update({'paho': paho, 'paho.mqtt': mqtt_pkg, 'paho.mqtt.client': mqtt})
spec = importlib.util.spec_from_file_location('experimental', Path(__file__).parents[1] / 'eltako2mqtt_experimental.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

class MQTT:
    def __init__(self): self.messages = []
    def publish(self, topic, payload, retain=False): self.messages.append((topic, payload, retain))

class Tests(unittest.IsolatedAsyncioTestCase):
    def bridge(self):
        b = module.ExperimentalBridge.__new__(module.ExperimentalBridge)
        b.pending_commands = {}; b._last_command_time = {}; b._recently_commanded_device = None
        b._command_timeout = 90; b.mqtt_client = MQTT()
        return b
    async def test_blind_feedback_does_not_mutate_hardware_state(self):
        b = self.bridge(); d = {'data':'eltako_blind','state':{'pos':20}}
        b._track_pending('01','80',d); await b._publish_command_feedback('01')
        self.assertEqual(d['state']['pos'],20); self.assertIn(('eltako/01/movement','closing',False),b.mqtt_client.messages)
    def test_polled_state_confirms_command(self):
        b = self.bridge(); d = {'data':'eltako_switch','state':{'state':'off'}}
        b._track_pending('11','on',d); b._reconcile_pending('11',{'data':'eltako_switch','state':{'state':'on'}})
        self.assertNotIn('11',b.pending_commands)
    def test_dimmer_expected_value(self):
        b = self.bridge(); d = {'data':'eltako_dimmer','state':{'state':'off','level':0}}
        b._track_pending('13','128',d)
        self.assertEqual(b.pending_commands['13']['expected'],{'state':'on','level':50})

if __name__ == '__main__': unittest.main()
