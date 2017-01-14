import unittest
from unittest.mock import patch, PropertyMock
from Firefly.automation.triggers import Trigger, Triggers
from Firefly.const import EVENT_ACTION_CLOSE, STATE, STATE_CLOSED, STATE_ON, EVENT_TYPE_BROADCAST, EVENT_ACTION_ANY, EVENT_ACTION_OPEN
from Firefly.helpers.subscribers import Subscriptions
from Firefly.helpers.events import Event


class TestTriggers(unittest.TestCase):
  @patch('Firefly.core.Firefly')
  def setUp(self, firefly):
    self.firefly = firefly
    self.firefly._subscriptions = Subscriptions()

  def test_building_trigger(self):
    trigger = Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)
    self.assertEqual(trigger.listen_id, 'listen_device')
    self.assertEqual(trigger.listen_action, EVENT_ACTION_CLOSE)
    self.assertEqual(trigger.request_property, STATE)
    self.assertEqual(trigger.request_verify, STATE_CLOSED)

    trigger_export = trigger.export()
    self.assertEqual(trigger_export, {'listen_id':      'listen_device', 'listen_action': 'CLOSE', 'request': 'STATE',
                                      'request_verify': 'CLOSED', 'source': 'SOURCE_TRIGGER'})

    trigger2 = Trigger(**trigger_export)
    trigger_export = trigger2.export()
    self.assertEqual(trigger_export, {'listen_id':      'listen_device', 'listen_action': 'CLOSE', 'request': 'STATE',
                                      'request_verify': 'CLOSED', 'source': 'SOURCE_TRIGGER'})
    # trigger1 and trigger2 should be equal to each other
    self.assertEqual(trigger, trigger2)

    self.assertNotEqual(trigger, Trigger('unknown'))

  def test_triggers(self):
    # with patch('Firefly.helpers.subscribers.Subscriptions.add_subscriber') as mock:
    # TODO: Get mock working to verify that add_subscriber is called

    triggers = Triggers(self.firefly, 'test_device')
    trigger = Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)
    added = triggers.add_trigger(trigger)
    self.assertTrue(added)
    self.assertEqual(triggers.triggers[0], trigger)

    added = triggers.add_trigger(trigger)
    self.assertFalse(added)

    removed = triggers.remove_trigger(trigger)
    self.assertTrue(removed)

    self.assertEqual(triggers.triggers, [])

    trigger = Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)
    triggers.add_trigger(trigger)
    trigger = Trigger('listen_device2', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)
    triggers.add_trigger(trigger)

    self.assertEqual(len(triggers.triggers), 2)

    trigger = [Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED),
               Trigger('listen_device2', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)]
    triggers.add_trigger(trigger)
    self.assertEqual(len(triggers.triggers), 3)

    triggers.add_trigger(trigger)
    self.assertEqual(len(triggers.triggers), 3)

    triggers.add_trigger(trigger)
    self.assertEqual(len(triggers.triggers), 3)

    trigger = [Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED),
               Trigger('listen_device2', EVENT_ACTION_CLOSE, STATE, STATE_ON)]

    triggers.add_trigger(trigger)
    self.assertEqual(len(triggers.triggers), 4)

    trigger = [Trigger('listen_device2', EVENT_ACTION_CLOSE, STATE, STATE_ON),
               Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)]

    triggers.add_trigger(trigger)
    self.assertEqual(len(triggers.triggers), 4)

    triggers.remove_trigger(trigger)
    self.assertEqual(len(triggers.triggers), 3)

    trigger = [Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED),
               Trigger('listen_device2', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)]
    triggers.remove_trigger(trigger)
    self.assertEqual(len(triggers.triggers), 2)

  def test_export_triggers(self):
    triggers = Triggers(self.firefly, 'test_device')
    trigger = Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)
    triggers.add_trigger(trigger)
    trigger = Trigger('listen_device2', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)
    triggers.add_trigger(trigger)

    export_data = triggers.export()
    expected_data = [
      {'listen_id': 'listen_device', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
       'source':    'SOURCE_TRIGGER'},
      {'listen_id': 'listen_device2', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
       'source':    'SOURCE_TRIGGER'}]
    self.assertEqual(export_data, expected_data)

    trigger = [Trigger('listen_device', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED),
               Trigger('listen_device2', EVENT_ACTION_CLOSE, STATE, STATE_ON)]

    triggers.add_trigger(trigger)

    export_data = triggers.export()
    expected_data = [
      {'listen_id': 'listen_device', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
       'source':    'SOURCE_TRIGGER'},
      {'listen_id': 'listen_device2', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
       'source':    'SOURCE_TRIGGER'},
      [
        {'listen_id': 'listen_device', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
         'source':    'SOURCE_TRIGGER'},
        {'listen_id': 'listen_device2', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'ON',
         'source':    'SOURCE_TRIGGER'}
      ]
    ]

    self.assertEqual(export_data, expected_data)

  def test_import_triggers(self):
    triggers = Triggers(self.firefly, 'test_device')

    import_data =  [
          {'listen_id': 'listen_device', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
           'source':    'SOURCE_TRIGGER'},
          {'listen_id': 'listen_device2', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
           'source':    'SOURCE_TRIGGER'}
    ]

    import_count = triggers.import_triggers(import_data)
    self.assertEqual(import_count, 2)
    self.assertEqual(len(triggers.triggers), 2)
    self.assertEqual(triggers.export(), import_data)

    # Test reimporting data twice
    import_count = triggers.import_triggers(import_data)
    self.assertEqual(import_count, 0)
    self.assertEqual(len(triggers.triggers), 2)
    self.assertEqual(triggers.export(), import_data)

    import_data = [
        {'listen_id': 'listen_device', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
         'source':    'SOURCE_TRIGGER'},
        {'listen_id': 'listen_device2', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
         'source':    'SOURCE_TRIGGER'},
        [
          {'listen_id': 'listen_device', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'CLOSED',
           'source':    'SOURCE_TRIGGER'},
          {'listen_id': 'listen_device2', 'listen_action': 'CLOSE', 'request': 'STATE', 'request_verify': 'ON',
           'source':    'SOURCE_TRIGGER'}
        ]
      ]

    import_count = triggers.import_triggers(import_data)
    self.assertEqual(import_count, 1)
    self.assertEqual(len(triggers.triggers), 3)
    self.assertEqual(triggers.export(), import_data)


  def test_check_trigger_one_simple(self):
    triggers = Triggers(self.firefly, 'test_device')
    trigger = Trigger('test_device2', EVENT_ACTION_CLOSE, STATE, STATE_CLOSED)
    triggers.add_trigger(trigger)

    event = Event('test_device2', EVENT_TYPE_BROADCAST, EVENT_ACTION_CLOSE)
    valid = triggers.check_triggers(event)
    self.assertTrue(valid)

    event = Event('test_device2', EVENT_TYPE_BROADCAST, EVENT_ACTION_OPEN)
    valid = triggers.check_triggers(event)
    self.assertFalse(valid)

    triggers = Triggers(self.firefly, 'test_device')
    trigger = Trigger('test_device2', EVENT_ACTION_CLOSE, STATE, EVENT_ACTION_ANY)
    triggers.add_trigger(trigger)

    event = Event('test_device2', EVENT_TYPE_BROADCAST, EVENT_ACTION_CLOSE)
    valid = triggers.check_triggers(event)
    self.assertTrue(valid)




