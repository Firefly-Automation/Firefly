import unittest
from unittest.mock import Mock, PropertyMock, patch

from Firefly.const import EVENT_ACTION_ANY, EVENT_ACTION_ON, EVENT_TYPE_BROADCAST, STATE
from Firefly.helpers.automation import Automation
from Firefly.helpers.events import Event

# TODO(zpriddy): These should be in const file
LABEL_TRIGGERS = 'triggers'
LABEL_ACTIONS = 'actions'
LABEL_CONDITIONS = 'conditions'
LABEL_DELAYS = 'delays'
LABEL_MESSAGES = 'messages'


class TestAutomationHelper(unittest.TestCase):
  @patch('Firefly.core.Firefly', new_callable=PropertyMock)
  def setUp(self, firefly):
    self.firefly = firefly
    self.package = 'test_package'
    self.event_handler = Mock(return_value=True)
    self.device = 'test_trigger_device'
    self.device_2 = 'test_trigger_device_2'

  def test_automation_1(self):
    metadata = {
      'interface': {
        LABEL_TRIGGERS: {
          'first_trigger': {
            'context': 'Initial trigger of automation'
          }
        },
        LABEL_ACTIONS: {
          'first_trigger': {
            'context': 'Initial trigger action'
          }
        }
      }
    }
    interface = {
      LABEL_TRIGGERS: {
        'first_trigger': [[{
          'trigger_action': [{
            EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
          }],
          'listen_id':    self.device,
          'source':       'SOURCE_TRIGGER'
        }]]
      },
      LABEL_ACTIONS: {
        'first_trigger':[]
      }
    }
    automation = Automation(self.firefly, self.package, self.event_handler, metadata, interface)

    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })

    executed = automation.event(event)
    self.assertTrue(executed)
    Mock.assert_called_once_with(self.event_handler, event, 'first_trigger')

  def test_automation_2(self):
    metadata = {
      'interface': {
        LABEL_TRIGGERS: {
          'first_trigger':  {
            'context': 'Initial trigger of automation'
          },
          'second_trigger': {
            'context': 'Delay trigger of automation'
          }
        }
      }
    }
    interface = {
      LABEL_TRIGGERS: {
        'first_trigger':  [[{
          'trigger_action': [{
            EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
          }],
          'listen_id':    self.device,
          'source':       'SOURCE_TRIGGER'
        }]],
        'second_trigger': [[{
          'trigger_action': [{
            EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
          }],
          'listen_id':    self.device_2,
          'source':       'SOURCE_TRIGGER'
        }]]
      }
    }
    automation = Automation(self.firefly, self.package, self.event_handler, metadata, interface)

    event = Event(self.device_2, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })

    executed = automation.event(event)
    self.assertTrue(executed)
    Mock.assert_called_once_with(self.event_handler, event, 'second_trigger')
    print(automation.export())
