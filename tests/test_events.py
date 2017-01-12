from Firefly.helpers.events import (Event, Command)
from Firefly.const import (EVENT_TYPE_UPDATE, EVENT_TYPE_COMMAND, EVENT_ACTION_ACTIVE, COMMAND_NOTIFY, COMMAND_SPEECH, ACTION_OFF)
import unittest
from unittest import mock
from unittest.mock import patch


class EventTest(unittest.TestCase):
  def test_new_event(self):
    e = Event('event_source', EVENT_TYPE_UPDATE, EVENT_ACTION_ACTIVE)
    self.assertAlmostEqual(e.source, 'event_source')

class CommandTest(unittest.TestCase):
  def test_new_command(self):
    with patch('Firefly.aliases.get_device_id') as mock:
      mock.return_value = 'to_device'
      c = Command('to_device', 'test_case', ACTION_OFF)
      self.assertEqual(c.device, 'to_device')
      self.assertTrue(c.simple_command)
      self.assertEqual(c.source, 'test_case')

  def test_notify_command(self):
    with patch('Firefly.aliases.get_device_id') as mock:
      mock.return_value = 'to_device'
      c = Command('to_device', 'test_case', {'message': 'my message'}, command_action=COMMAND_NOTIFY)
      self.assertTrue(c.notify)
      self.assertEquals(c.event_type, EVENT_TYPE_COMMAND)
      self.assertFalse(c.simple_command)
      self.assertDictEqual(c.command, {'message': 'my message'})

  def test_speech(self):
    with patch('Firefly.aliases.get_device_id') as mock:
      mock.return_value = 'to_device'
      c = Command('to_device', 'test_case', {'message': 'my message'}, command_action=COMMAND_SPEECH)
      self.assertTrue(c.speech)