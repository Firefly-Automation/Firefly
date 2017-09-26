import unittest
from unittest.mock import patch

from Firefly.automation.triggers import Trigger, Triggers
from Firefly.const import EVENT_ACTION_ANY, EVENT_ACTION_OFF, EVENT_ACTION_ON, EVENT_SUNRISE, EVENT_SUNSET, EVENT_TYPE_BROADCAST, SOURCE_LOCATION, STATE, TIME
from Firefly.helpers.events import Event
from Firefly.helpers.subscribers import Subscriptions


class TestTriggers(unittest.TestCase):
  @patch('Firefly.core.Firefly')
  def setUp(self, firefly):
    self.firefly = firefly
    self.firefly.subscriptions = Subscriptions()
    self.device = 'fake_device'
    self.device_b = 'fake_device_b'
    self.app = 'subscriber_app'
    self.app_b = 'subscriber_app_b'
    self.trigger_id = 'test_automation_trigger'

  def test_trigger_simple(self):
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    self.assertListEqual(trigger.trigger_action, [{
      STATE: [EVENT_ACTION_ON]
    }])
    self.assertEquals(trigger.listen_id, self.device)

  def test_trigger_any(self):
    trigger = Trigger(self.device)
    self.assertListEqual(trigger.trigger_action, [{
      EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
    }])
    self.assertEquals(trigger.listen_id, self.device)

  def test_trigger_any_property(self):
    trigger = Trigger(self.device, {
      EVENT_ACTION_ANY: [EVENT_ACTION_ON]
    })
    self.assertListEqual(trigger.trigger_action, [{
      EVENT_ACTION_ANY: [EVENT_ACTION_ON]
    }])
    self.assertEquals(trigger.listen_id, self.device)

  def test_trigger_any_source(self):
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    self.assertListEqual(trigger.trigger_action, [{
      STATE: [EVENT_ACTION_ON]
    }])
    self.assertEquals(trigger.listen_id, self.device)

  def test_add_one_trigger(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])

    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device})

  def test_add_one_trigger_twice(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger(trigger)
    self.assertFalse(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device})

  def test_add_one_trigger_list(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger2 = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger([trigger, trigger2])
    self.assertTrue(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }, {
      'listen_id':      self.device_b,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device, self.device_b})

  def test_add_one_trigger_list_twice(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger2 = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger([trigger, trigger2])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger([trigger, trigger2])
    self.assertFalse(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }, {
      'listen_id':      self.device_b,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device, self.device_b})

  def test_add_one_trigger_list_twice_reorder(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger2 = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger([trigger, trigger2])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger([trigger2, trigger])
    self.assertFalse(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }, {
      'listen_id':      self.device_b,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })

  def test_add_one_trigger_case_1(self):
    '''
    This test adding a trigger that's a subset of another trigger.
    '''
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger2 = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger([trigger, trigger2])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger([trigger])
    self.assertTrue(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }, {
      'listen_id':      self.device_b,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }], [{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device, self.device_b})

  def test_add_any_trigger(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device)
    trigger_added = triggers.add_trigger([trigger])
    self.assertTrue(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device})

  def test_add_any_property_trigger(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ANY]
    })
    trigger_added = triggers.add_trigger([trigger])
    self.assertTrue(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ANY]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ANY: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device})

  @unittest.skip
  def test_remove_trigger_one(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    removed = triggers.remove_trigger(trigger)
    self.assertTrue(removed, 'Trigger not removed')
    self.assertListEqual(triggers.triggers, [])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON: []
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, set())

  @unittest.skip
  def test_remove_trigger_shared_subscriptions_case_1(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    trigger_a = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger([trigger_a, trigger_b])
    self.assertTrue(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }], [{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }, {
      'listen_id':      self.device_b,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    removed = triggers.remove_trigger(trigger)
    self.assertTrue(removed)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }, {
      'listen_id':      self.device_b,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device, self.device_b})

  @unittest.skip
  def test_remove_trigger_shared_subscriptions_case_2(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    trigger_a = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger([trigger_a, trigger_b])
    self.assertTrue(trigger_added)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }], [{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }, {
      'listen_id':      self.device_b,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    removed = triggers.remove_trigger([trigger_a, trigger_b])
    self.assertTrue(removed)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: []
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device})

  @unittest.skip
  def test_remove_trigger_non_existant(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    trigger_a = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger([trigger_a, trigger_b])
    self.assertTrue(trigger_added)
    removed = triggers.remove_trigger(trigger_b)
    self.assertFalse(removed)
    self.assertListEqual(triggers.triggers, [[{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }], [{
      'listen_id':      self.device,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }, {
      'listen_id':      self.device_b,
      'trigger_action': [{
        STATE: [EVENT_ACTION_ON]
      }],
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertDictEqual(self.firefly.subscriptions.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON: [self.trigger_id]
        }
      }
    })
    self.assertSetEqual(triggers.trigger_sources, {self.device, self.device_b})

  def test_check_triggers_case_1(self):
    """Valid Trigger"""
    # Data returned for current_states
    data = {
      self.device: {
        STATE: EVENT_ACTION_ON
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_2(self):
    """Event not in triggers"""
    # Data returned for current_states
    data = {
      self.device: {
        STATE: EVENT_ACTION_ON
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device_b, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertFalse(triggered)

  def test_check_triggers_case_3(self):
    """Trigger of two devices. Invalid Trigger"""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_ON
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger, trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertFalse(triggered)

  def test_check_triggers_case_4(self):
    """Trigger of two devices. Valid Trigger."""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger, trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_5(self):
    """2 Triggers of one devices. Valid Trigger."""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger([trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_6(self):
    """2 Triggers of one devices. Reordered Valid Trigger."""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger([trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device_b, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_OFF
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_7(self):
    """2 Triggers of one devices. Invalid Trigger."""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_ON
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger([trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device_b, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertFalse(triggered)

  def test_check_triggers_case_8(self):
    """2 Triggers of one devices, overwrite current_states with trigger value. Valid Trigger."""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_ON
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger([trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device_b, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_OFF
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_9(self):
    """2 Triggers of one devices, overwrite current_states with trigger value, but told to ignore event. Invalid
    Trigger."""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_ON
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger([trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device_b, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_OFF
    })
    triggered = triggers.check_triggers(event, ignore_event=True)
    self.assertFalse(triggered)

  def test_check_triggers_case_10(self):
    """Test error of improper current_states"""
    # Data returned for current_states
    data = {
      self.device_b: {
        STATE: EVENT_ACTION_ON
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger, trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device_b, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertFalse(triggered)

  def test_check_triggers_case_11(self):
    """Test trigger ANY. Valid Trigger"""
    # Data returned for current_states
    data = {}

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device)
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_12(self):
    """Test trigger ANY. Valid Trigger"""
    # Data returned for current_states
    data = {}

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_13(self):
    """Test trigger ANY. Valid Trigger"""
    # Data returned for current_states
    data = {}

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      EVENT_ACTION_ANY: [EVENT_ACTION_ANY],
      STATE:            [EVENT_ACTION_ON]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_14(self):
    """Test trigger ANY. Valid Trigger"""
    # Data returned for current_states
    data = {}

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ANY]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_ON
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_15(self):
    """2 Triggers of one devices, overwrite current_states with trigger value, but told to ignore event. Invalid
    Trigger."""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_added = triggers.add_trigger([trigger, trigger_b])
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      STATE: EVENT_ACTION_OFF
    })
    self.firefly.update_current_state(event)
    triggered = triggers.check_triggers(event, ignore_event=True)
    self.assertTrue(triggered)

  def test_check_triggers_case_16(self):
    """Verify trigger any of property only"""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ANY
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ANY]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(self.device, EVENT_TYPE_BROADCAST, {
      'MOTION': 'ACTIVE'
    })
    triggered = triggers.check_triggers(event)
    self.assertFalse(triggered)

  def test_check_triggers_case_17(self):
    """Verify location triggers"""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ANY
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(SOURCE_LOCATION, {
      SOURCE_LOCATION: [EVENT_SUNSET]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, {
      SOURCE_LOCATION: EVENT_SUNSET
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_case_18(self):
    """Verify location triggers"""
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ANY
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(SOURCE_LOCATION, {
      SOURCE_LOCATION: [EVENT_SUNSET]
    })
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, {
      SOURCE_LOCATION: EVENT_SUNRISE
    })
    triggered = triggers.check_triggers(event)
    self.assertFalse(triggered)

  def test_export_trigger_case_1(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device)
    triggers.add_trigger(trigger)
    export_data = triggers.export()
    self.assertListEqual(export_data, [[{
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }]])

  def test_export_trigger_case_2(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, [EVENT_ACTION_ON, EVENT_ACTION_OFF])
    triggers.add_trigger(trigger)
    export_data = triggers.export()
    self.assertListEqual(export_data, [[{
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }]])

  def test_export_trigger_case_3(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device)
    trigger_b = Trigger(self.device_b)
    triggers.add_trigger([trigger, trigger_b])
    self.assertSetEqual(triggers.trigger_sources, {self.device, self.device_b})
    export_data = triggers.export()
    self.assertListEqual(export_data, [[{
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }, {
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device_b,
      'source':         'SOURCE_TRIGGER'
    }]])

  def test_export_trigger_case_4(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ANY]
    })
    triggers.add_trigger(trigger)
    export_data = triggers.export()
    self.assertListEqual(export_data, [[{
      'trigger_action': [{
        STATE: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }]])

  def test_export_trigger_case_5(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ANY]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ANY]
    })
    triggers.add_trigger(trigger)
    triggers.add_trigger(trigger_b)
    export_data = triggers.export()
    self.assertListEqual(export_data, [[{
      'trigger_action': [{
        STATE: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }], [{
      'trigger_action': [{
        STATE: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device_b,
      'source':         'SOURCE_TRIGGER'
    }]])

  def test_import_trigger_case_1(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    import_data = [[{
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }]]
    count = triggers.import_triggers(import_data)
    self.assertEquals(count, 1)
    self.assertSetEqual(triggers.trigger_sources, {self.device})
    export_data = triggers.export()
    self.assertListEqual(export_data, import_data)

  def test_import_trigger_case_2(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    import_data = [[{
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }]]
    count = triggers.import_triggers(import_data)
    self.assertEquals(count, 1)
    self.assertSetEqual(triggers.trigger_sources, {self.device})
    export_data = triggers.export()
    self.assertListEqual(export_data, import_data)

  def test_import_trigger_case_3(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    import_data = [[{
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }, {
      'trigger_action': [{
        EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device_b,
      'source':         'SOURCE_TRIGGER'
    }]]
    count = triggers.import_triggers(import_data)
    self.assertEquals(count, 1)
    self.assertSetEqual(triggers.trigger_sources, {self.device, self.device_b})
    export_data = triggers.export()
    self.assertListEqual(export_data, import_data)

  def test_import_trigger_case_4(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    import_data = [[{
      'trigger_action': [{
        STATE: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }]]
    count = triggers.import_triggers(import_data)
    self.assertEquals(count, 1)
    self.assertSetEqual(triggers.trigger_sources, {self.device})
    export_data = triggers.export()
    self.assertListEqual(export_data, import_data)

  def test_import_trigger_case_5(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    import_data = [[{
      'trigger_action': [{
        STATE: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device,
      'source':         'SOURCE_TRIGGER'
    }], [{
      'trigger_action': [{
        STATE: [EVENT_ACTION_ANY]
      }],
      'listen_id':      self.device_b,
      'source':         'SOURCE_TRIGGER'
    }]]
    count = triggers.import_triggers(import_data)
    self.assertEquals(count, 2)
    self.assertSetEqual(triggers.trigger_sources, {self.device, self.device_b})
    export_data = triggers.export()
    self.assertListEqual(export_data, import_data)

  # TIME TRIGGERS
  def test_trigger_time_case_1(self):
    trigger = Trigger(TIME, {
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    })
    self.assertListEqual(trigger.trigger_action, [{
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    }])
    self.assertEquals(trigger.listen_id, TIME)

  def test_trigger_time_case_2(self):
    trigger = Trigger(TIME, [{
      'hour':     7,
      'minute':   00,
      'weekdays': [5, 6, 7]
    }, {
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    }])
    self.assertListEqual(trigger.trigger_action, [{
      'hour':     7,
      'minute':   00,
      'weekdays': [5, 6, 7]
    }, {
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    }])
    self.assertEquals(trigger.listen_id, TIME)

  def test_check_time_trigger(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    event = Event(TIME, EVENT_TYPE_BROADCAST, {
      'epoch':   1491076620.683116,
      'day':     1,
      'month':   4,
      'year':    2017,
      'hour':    6,
      'minute':  00,
      'weekday': 1
    })
    trigger = Trigger(TIME, [{
      'hour':     6,
      'minute':   0,
      'weekdays': [1, 2, 3, 4]
    }])
    added = triggers.add_trigger(trigger)
    self.assertTrue(added)
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_time_case_1(self):
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_ON
      },
      self.device_b: {
        STATE: EVENT_ACTION_ON
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_c = Trigger(TIME, {
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    })
    trigger_added = triggers.add_trigger([trigger, trigger_b])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger(trigger_c)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(TIME, EVENT_TYPE_BROADCAST, {
      'epoch':   1491076620.683116,
      'day':     1,
      'month':   4,
      'year':    2017,
      'hour':    6,
      'minute':  00,
      'weekday': 1
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_time_case_2(self):
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_OFF
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_OFF]
    })
    trigger_c = Trigger(TIME, {
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    })
    trigger_added = triggers.add_trigger([trigger_c, trigger_b])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(TIME, EVENT_TYPE_BROADCAST, {
      'epoch':   1491076620.683116,
      'day':     1,
      'month':   4,
      'year':    2017,
      'hour':    6,
      'minute':  00,
      'weekday': 1
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_time_case_3(self):
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_OFF
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_c = Trigger(TIME, {
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    })
    trigger_added = triggers.add_trigger([trigger_c, trigger_b])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(TIME, EVENT_TYPE_BROADCAST, {
      'epoch':   1491076620.683116,
      'day':     1,
      'month':   4,
      'year':    2017,
      'hour':    6,
      'minute':  00,
      'weekday': 1
    })
    triggered = triggers.check_triggers(event)
    self.assertFalse(triggered)

  def test_check_triggers_time_case_4(self):
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_OFF
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(self.device_b, {
      STATE: [EVENT_ACTION_ANY]
    })
    trigger_c = Trigger(TIME, {
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    })
    trigger_added = triggers.add_trigger([trigger_c, trigger_b])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(TIME, EVENT_TYPE_BROADCAST, {
      'epoch':   1491076620.683116,
      'day':     1,
      'month':   4,
      'year':    2017,
      'hour':    6,
      'minute':  00,
      'weekday': 1
    })
    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)

  def test_check_triggers_time_case_5(self):
    # Data returned for current_states
    data = {
      self.device:   {
        STATE: EVENT_ACTION_OFF
      },
      self.device_b: {
        STATE: EVENT_ACTION_OFF
      }
    }

    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    trigger_b = Trigger(TIME, {
      'hour':     8,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    })
    trigger_c = Trigger(TIME, {
      'hour':     6,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    })
    trigger_added = triggers.add_trigger([trigger_c, trigger_b])
    self.assertTrue(trigger_added)
    trigger_added = triggers.add_trigger(trigger)
    self.assertTrue(trigger_added)
    self.firefly.current_state = data
    event = Event(TIME, EVENT_TYPE_BROADCAST, {
      'epoch':   1491076620.683116,
      'day':     1,
      'month':   4,
      'year':    2017,
      'hour':    8,
      'minute':  00,
      'weekday': 1
    })
    triggered = triggers.check_triggers(event)
    self.assertFalse(triggered)

  def test_export_trigger_time(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    trigger = Trigger(TIME, {
      'hour':     8,
      'minute':   00,
      'weekdays': [1, 2, 3, 4]
    })
    triggers.add_trigger(trigger)
    export_data = triggers.export()
    self.assertListEqual(export_data, [[{
      'trigger_action': [{
        'hour':     8,
        'minute':   00,
        'weekdays': [1, 2, 3, 4]
      }],
      'listen_id':      TIME,
      'source':         'SOURCE_TRIGGER'
    }]])

  def test_import_trigger_time(self):
    triggers = Triggers(self.firefly, self.trigger_id)
    import_data = [[{
      'trigger_action': [{
        'hour':     8,
        'minute':   00,
        'weekdays': [1, 2, 3, 4]
      }],
      'listen_id':      TIME,
      'source':         'SOURCE_TRIGGER'
    }]]
    count = triggers.import_triggers(import_data)
    self.assertListEqual(triggers.triggers, [[{
      'trigger_action': [{
        'hour':     8,
        'minute':   00,
        'weekdays': [1, 2, 3, 4]
      }],
      'listen_id':      TIME,
      'source':         'SOURCE_TRIGGER'
    }]])
    self.assertEquals(count, 1)
    self.assertSetEqual(triggers.trigger_sources, {TIME})
    export_data = triggers.export()
    self.assertListEqual(export_data, import_data)
    self.assertEquals(export_data[0][0]['trigger_action'][0]['hour'], 8)
    event = Event(TIME, EVENT_TYPE_BROADCAST, {
      'epoch':   1491076620.683116,
      'day':     1,
      'month':   4,
      'year':    2017,
      'hour':    8,
      'minute':  00,
      'weekday': 1
    })

    triggered = triggers.check_triggers(event)
    self.assertTrue(triggered)
