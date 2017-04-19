import unittest

from Firefly.helpers.subscribers import Subscriptions, verify_event_action
from Firefly.const import (EVENT_ACTION_ANY, EVENT_PROPERTY_ANY, EVENT_ACTION_ON, EVENT_ACTION_OFF, STATE,
                           EVENT_ACTION_OFF, EVENT_ACTION_ON)


class VerifyEventActions(unittest.TestCase):
  def test_any_string(self):
    event_action = EVENT_ACTION_ANY
    verify = verify_event_action(event_action)
    self.assertEquals(verify, [{
      EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
    }])

  def test_any_list(self):
    event_action = [EVENT_ACTION_ANY]
    verify = verify_event_action(event_action)
    self.assertEquals(verify, [{
      EVENT_ACTION_ANY: [EVENT_ACTION_ANY]
    }])

  def test_single_event_action(self):
    event_action = {
      STATE: EVENT_ACTION_OFF
    }
    verify = verify_event_action(event_action)
    self.assertEquals(verify, [{
      STATE: [EVENT_ACTION_OFF]
    }])

  def test_single_event_list(self):
    event_action = [{
      STATE: EVENT_ACTION_OFF
    }]
    verify = verify_event_action(event_action)
    self.assertEquals(verify, [{
      STATE: [EVENT_ACTION_OFF]
    }])

  def test_two_event_action(self):
    event_action = {
      STATE: [EVENT_ACTION_OFF, EVENT_ACTION_ON]
    }
    verify = verify_event_action(event_action)
    self.assertEquals(verify, [{
      STATE: [EVENT_ACTION_OFF, EVENT_ACTION_ON]
    }])

  def test_two_event_action_list(self):
    event_action = [{
      STATE: [EVENT_ACTION_OFF, EVENT_ACTION_ON]
    }]
    verify = verify_event_action(event_action)
    self.assertEquals(verify, [{
      STATE: [EVENT_ACTION_OFF, EVENT_ACTION_ON]
    }])

  def test_any_single(self):
    event_action = {
      EVENT_PROPERTY_ANY: [EVENT_ACTION_OFF]
    }
    verify = verify_event_action(event_action)
    self.assertEquals(verify, [{
      EVENT_ACTION_ANY: [EVENT_ACTION_OFF]
    }])


class SubscribersTest(unittest.TestCase):
  def setUp(self):
    self.device = 'fake_device'
    self.device_b = 'fake_device_b'
    self.app = 'subscriber_app'
    self.app_b = 'subscriber_app_b'

  def test_add_subscriber_any(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.app]
        }
      }
    })

  def test_add_subscriber_custom_any(self):
    """This test would be an app listening to any change of property custom.

    An example of this would be a light switch and an app that wants to trigger when the value of switch is changed.
    This would be event_action={STATE:EVENT_ACTION_ANY}
    """
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      'CUSTOM': EVENT_ACTION_ANY
    })
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        'CUSTOM': {
          EVENT_ACTION_ANY: [self.app]
        }
      }
    })

  def test_add_subscriber_any_custom(self):
    """This would test an app listening any change that the value is 'CUSTOM'

    An example of this would be a powerstrip with multiple controllable outlets and an app that wants to be triggered
    when any of them turn on. This would be event_action={EVENT_PROPERTY_ANY:ACTION_ON}
    """
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      EVENT_PROPERTY_ANY: 'CUSTOM'
    })
    s.add_subscriber(self.app, self.device, event_action={
      EVENT_PROPERTY_ANY: 'CUSTOM'
    })
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        EVENT_PROPERTY_ANY: {
          'CUSTOM': [self.app]
        }
      }
    })

  def test_add_subscriber_multiple_event_action_same_property(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [self.app],
          EVENT_ACTION_OFF: [self.app]
        }
      }
    })

  def test_add_multiple_subscribers_any(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device)
    s.add_subscriber(self.app_b, self.device)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.app, self.app_b]
        }
      }
    })

  def test_add_multiple_subscribers_different_apps(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action=[EVENT_ACTION_ON])
    s.add_subscriber(self.app_b, self.device, event_action=[EVENT_ACTION_OFF])
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ON:  [self.app],
          EVENT_ACTION_OFF: [self.app_b]
        }
      }
    })

  def test_multiple_listen_to_any(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device)
    s.add_subscriber(self.app, self.device_b)
    self.assertDictEqual(s.subscriptions, {
      self.device:   {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.app]
        }
      },
      self.device_b: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.app]
        }
      }
    })

  def test_get_all_subscribers_any(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device)
    s.add_subscriber(self.app, self.device_b)
    self.assertDictEqual(s.subscriptions, {
      self.device:   {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.app]
        }
      },
      self.device_b: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.app]
        }
      }
    })
    subs = s.get_all_subscribers(self.device)
    self.assertSetEqual(set(subs), {self.app})

  def test_get_all_subscribers_any_two(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device)
    s.add_subscriber(self.app_b, self.device)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.app, self.app_b]
        }
      }
    })
    subs = s.get_all_subscribers(self.device)
    self.assertSetEqual(set(subs), {self.app, self.app_b})

  def test_get_all_subscribers_one(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [self.app],
          EVENT_ACTION_OFF: [self.app]
        }
      }
    })
    subs = s.get_all_subscribers(self.device)
    self.assertSetEqual(set(subs), {self.app})

  def test_get_all_subscribers_two(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action=[EVENT_ACTION_ON])
    s.add_subscriber(self.app_b, self.device, event_action=[EVENT_ACTION_OFF])
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ON:  [self.app],
          EVENT_ACTION_OFF: [self.app_b]
        }
      }
    })
    subs = s.get_all_subscribers(self.device)
    self.assertSetEqual(set(subs), {self.app, self.app_b})

  def test_get_subscriber_items(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action=[EVENT_ACTION_ON])
    s.add_subscriber(self.app, self.device)
    s.add_subscriber(self.app_b, self.device, event_action=[EVENT_ACTION_OFF])
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ON:  [self.app],
          EVENT_ACTION_OFF: [self.app_b],
          EVENT_ACTION_ANY: [self.app]
        }
      }
    })
    items = s.get_subscriber_items(self.app, self.device)
    self.assertEqual(items, {
      EVENT_ACTION_ANY: {
        EVENT_ACTION_ON:  True,
        EVENT_ACTION_ANY: True
      }
    })

  # DELETE SUBSCRIBER TESTS
  def test_delete_subscription_simple(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    delete_count = s.delete_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON]
    })
    self.assertEqual(delete_count, 1)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [],
          EVENT_ACTION_OFF: [self.app]
        }
      }
    })

  def test_delete_subscription_simple_all(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    delete_count = s.delete_subscriber(self.app, self.device, delete_all=True)
    self.assertEqual(delete_count, 2)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [],
          EVENT_ACTION_OFF: []
        }
      }
    })

  def test_delete_subscription_non_existant_all(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    delete_count = s.delete_subscriber(self.app, self.device_b, delete_all=True)
    self.assertEqual(delete_count, 0)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [self.app],
          EVENT_ACTION_OFF: [self.app]
        }
      }
    })

  def test_delete_subscription_non_existant(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    delete_count = s.delete_subscriber(self.app, self.device_b, event_action={
      STATE: [EVENT_ACTION_ON]
    })
    self.assertEqual(delete_count, 0)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [self.app],
          EVENT_ACTION_OFF: [self.app]
        }
      }
    })

  def test_delete_subscription_simple_twice(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    delete_count = s.delete_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON]
    })
    self.assertEqual(delete_count, 1)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [],
          EVENT_ACTION_OFF: [self.app]
        }
      }
    })
    delete_count = s.delete_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON]
    })
    self.assertEqual(delete_count, 0)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [],
          EVENT_ACTION_OFF: [self.app]
        }
      }
    })

  def test_delete_subscription_simple_all_twice(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    delete_count = s.delete_subscriber(self.app, self.device, delete_all=True)
    self.assertEqual(delete_count, 2)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [],
          EVENT_ACTION_OFF: []
        }
      }
    })
    delete_count = s.delete_subscriber(self.app, self.device, delete_all=True)
    self.assertEqual(delete_count, 0)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_ON:  [],
          EVENT_ACTION_OFF: []
        }
      }
    })

  def test_delete_all_subscription(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    s.add_subscriber(self.app, self.device_b, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    s.add_subscriber(self.app_b, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    delete_count = s.delete_all_subscriptions(self.app)
    self.assertEquals(delete_count, 4)
    self.assertDictEqual(s.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_ON:  [self.app_b],
          EVENT_ACTION_OFF: [self.app_b]
        }
      },
      self.device_b: {
        STATE: {
          EVENT_ACTION_ON:  [],
          EVENT_ACTION_OFF: []
        }
      }
    })

  def test_change_parent_id(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    c = s.change_subscriber_parent_id(self.device, self.device_b)
    self.assertTrue(c)
    self.assertDictEqual(s.subscriptions, {
      self.device_b: {
        STATE: {
          EVENT_ACTION_OFF: [self.app],
          EVENT_ACTION_ON:  [self.app]
        }
      }
    })

  def test_change_subscriber_id(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    count = s.change_subscriber_id(self.app, self.app_b)
    self.assertEqual(count, 2)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_OFF: [self.app_b],
          EVENT_ACTION_ON:  [self.app_b]
        }
      }
    })

  def test_change_subscriber_id_complex(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    s.add_subscriber(self.app, self.device_b)
    count = s.change_subscriber_id(self.app, self.app_b)
    self.assertEqual(count, 3)
    self.assertDictEqual(s.subscriptions, {
      self.device:   {
        STATE: {
          EVENT_ACTION_OFF: [self.app_b],
          EVENT_ACTION_ON:  [self.app_b]
        }
      },
      self.device_b: {
        EVENT_ACTION_ANY: {
          EVENT_ACTION_ANY: [self.app_b]
        }
      }
    })

  def test_change_subscriber_id_none_existant(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, event_action={
      STATE: [EVENT_ACTION_ON, EVENT_ACTION_OFF]
    })
    count = s.change_subscriber_id(self.app_b, self.app)
    self.assertEqual(count, 0)
    self.assertDictEqual(s.subscriptions, {
      self.device: {
        STATE: {
          EVENT_ACTION_OFF: [self.app],
          EVENT_ACTION_ON:  [self.app]
        }
      }
    })

  def test_get_subscribers_any(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device)
    subscribers = s.get_subscribers(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    self.assertListEqual(subscribers, [self.app])

  def test_get_subscribers_none(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device)
    subscribers = s.get_subscribers(self.device_b, {
      STATE: [EVENT_ACTION_ON]
    })
    self.assertListEqual(subscribers, [])

  def test_get_subscribers_no_event(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device)
    subscribers = s.get_subscribers(self.device)
    self.assertListEqual(subscribers, [self.app])

  def test_get_subscribers_two(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, {
      STATE: [EVENT_ACTION_ANY]
    })
    s.add_subscriber(self.app_b, self.device, {
      STATE: [EVENT_ACTION_OFF]
    })
    subscribers = s.get_subscribers(self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    self.assertListEqual(subscribers, [self.app])
    subscribers = s.get_subscribers(self.device, {
      STATE: [EVENT_ACTION_OFF]
    })
    self.assertSetEqual(set(subscribers), {self.app, self.app_b})

  def test_get_subscribers_multiple_events(self):
    s = Subscriptions()
    s.add_subscriber(self.app, self.device, {
      STATE: [EVENT_ACTION_ON]
    })
    s.add_subscriber(self.app_b, self.device, {
      STATE: [EVENT_ACTION_OFF]
    })
    subscribers = s.get_subscribers(self.device, {
      STATE: [EVENT_ACTION_OFF, EVENT_ACTION_ON]
    })
    self.assertSetEqual(set(subscribers), {self.app, self.app_b})
