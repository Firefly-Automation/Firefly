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
  @patch('Firefly.core.core.Firefly', new_callable=PropertyMock)
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
        LABEL_ACTIONS:  {
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
          'listen_id':      self.device,
          'source':         'SOURCE_TRIGGER'
        }]]
      },
      LABEL_ACTIONS:  {
        'first_trigger': []
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
      "author":    "Zachary Priddy (me@zpriddy.com)",
      "commands":  [
        "execute"
      ],
      "interface": {
        "actions":    {
          "delayed": {
            "context": "Actions to be executed when on delayed trigger.",
            "type":    "commandList"
          },
          "initial": {
            "context": "Actions to be executed when on initial trigger.",
            "type":    "commandList"
          }
        },
        "conditions": {
          "delayed": {
            "context": "Condition for delayed trigger.",
            "type":    "condition"
          },
          "initial": {
            "context": "Condition for initial trigger.",
            "type":    "condition"
          }
        },
        "delays":     {
          "delayed": {
            "context": "Time to delay after delayed trigger is triggered before executing actions. (seconds)",
            "type":    "number"
          },
          "initial": {
            "context": "Time to delay before initial actions are executed. (seconds)",
            "type":    "number"
          }
        },
        "messages":   {
          "delayed": {
            "context": "Message to be sent on delayed trigger.",
            "type":    "string"
          },
          "initial": {
            "context": "Message to be sent on initial trigger.",
            "type":    "string"
          }
        },
        "triggers":   {
          "delayed": {
            "context": "Triggers to trigger the delayed actions.",
            "type":    "triggerList"
          },
          "initial": {
            "context": "Triggers to initially trigger the initial actions.",
            "type":    "triggerList"
          }
        }
      },
      "title":     "Firefly Simple Rule"
    }
    interface = {
      "actions":    {
        "delayed": [
          {
            "command":    "on",
            "conditions": {},
            "ff_id":      "fec13065-cb28-48c3-9809-dc2c3abac865",
            "force":      False,
            "source":     "temp_window_fan_control"
          },
          {
            "command":    "on",
            "conditions": {},
            "ff_id":      "7809910a-bb22-460e-a07f-885ef42ac3d8",
            "force":      False,
            "source":     "temp_window_fan_control"
          }
        ],
        "initial": [
          {
            "command":    "off",
            "conditions": {},
            "ff_id":      "fec13065-cb28-48c3-9809-dc2c3abac865",
            "force":      False,
            "source":     "temp_window_fan_control"
          },
          {
            "command":    "off",
            "conditions": {},
            "ff_id":      "7809910a-bb22-460e-a07f-885ef42ac3d8",
            "force":      False,
            "source":     "temp_window_fan_control"
          }
        ]
      },
      "conditions": {
        "delayed": {
          "is_mode": ["home"]
        }
      },
      "delays":     {
        "delayed": 60
      },
      "devices":    {},
      "messages":   {},
      "triggers":   {
        "delayed": [
          [
            {
              "listen_id":      "4f99f740-a03f-44ce-b872-2325da7604be",
              "source":         "SOURCE_TRIGGER",
              "trigger_action": [
                {
                  "temperature": [
                    {
                      "gt": 68
                    }
                  ]
                }
              ]
            }
          ]
        ],
        "initial": [
          [
            {
              "listen_id":      "4f99f740-a03f-44ce-b872-2325da7604be",
              "source":         "SOURCE_TRIGGER",
              "trigger_action": [
                {
                  "temperature": [
                    {
                      "le": 66
                    }
                  ]
                }
              ]
            }
          ]
        ]
      }
    }
    automation = Automation(self.firefly, self.package, self.event_handler, metadata, interface)

    event = Event("4f99f740-a03f-44ce-b872-2325da7604be", EVENT_TYPE_BROADCAST, {
      "temperature": 65
    })

    executed = automation.event(event)
    self.assertTrue(executed)
    Mock.assert_called_once_with(self.event_handler, event, 'initial')


