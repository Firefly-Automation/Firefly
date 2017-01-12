import unittest

from Firefly.helpers.subscribers import Subscriptions
from Firefly.const import (EVENT_ACTION_ANY, EVENT_ACTION_ON, EVENT_ACTION_OFF)


class SubscribersTest(unittest.TestCase):
  def test_add_subscriber_any(self):
    s = Subscriptions()
    s.add_subscriber('subscriber', 'listen_to')
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_ANY: ['subscriber']}})

  def test_add_subscriber_custom(self):
    s = Subscriptions()
    s.add_subscriber('subscriber', 'listen_to', event_action=['CUSTOM'])
    self.assertEqual(s.subscriptions, {'listen_to': {'CUSTOM': ['subscriber']}})

  def test_add_subscriber_multiple_event_action(self):
    s = Subscriptions()
    s.add_subscriber('subscriber', 'listen_to', event_action=[EVENT_ACTION_ON, EVENT_ACTION_OFF])
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_ON: ['subscriber'], EVENT_ACTION_OFF: ['subscriber']}})

  def test_add_multiple_subscribers_any(self):
    s = Subscriptions()
    s.add_subscriber('subscriber1', 'listen_to')
    s.add_subscriber('subscriber2', 'listen_to')
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_ANY: ['subscriber1', 'subscriber2']}})

  def test_add_multiple_subscribers_different(self):
    s = Subscriptions()
    s.add_subscriber('subscriber1', 'listen_to', event_action=[EVENT_ACTION_ON])
    s.add_subscriber('subscriber2', 'listen_to', event_action=[EVENT_ACTION_OFF])
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_ON: ['subscriber1'], EVENT_ACTION_OFF: ['subscriber2']}})

  def test_multiple_listen_to(self):
    s = Subscriptions()
    s.add_subscriber('subscriber', 'listen_to1')
    s.add_subscriber('subscriber', 'listen_to2')
    self.assertEqual(s.subscriptions,
                     {'listen_to1': {EVENT_ACTION_ANY: ['subscriber']}, 'listen_to2': {EVENT_ACTION_ANY: ['subscriber']}})

  def test_delete_subscription(self):
    # Create new subscriptions.
    s = Subscriptions()
    s.add_subscriber('subscriber', 'listen_to', event_action=[EVENT_ACTION_ON, EVENT_ACTION_OFF])
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_ON: ['subscriber'], EVENT_ACTION_OFF: ['subscriber']}})

    # Delete one subscription.
    delete_count = s.delete_subscriber('subscriber', 'listen_to', event_action=[EVENT_ACTION_ON])
    self.assertEqual(delete_count, 1)
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_ON: [], EVENT_ACTION_OFF: ['subscriber']}})

    # Add subscriber back in.
    s.add_subscriber('subscriber', 'listen_to', event_action=[EVENT_ACTION_ON, EVENT_ACTION_OFF])
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_ON: ['subscriber'], EVENT_ACTION_OFF: ['subscriber']}})

    # Delete all subscriptions.
    delete_count = s.delete_subscriber('subscriber', 'listen_to', all=True)
    self.assertEqual(delete_count, 2)
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_ON: [], EVENT_ACTION_OFF: []}})

  def test_get_subscribers(self):
    s = Subscriptions()
    s.add_subscriber('subscriber1', 'listen_to', event_action=[EVENT_ACTION_OFF])
    s.add_subscriber('subscriber2', 'listen_to', event_action=[EVENT_ACTION_ON, EVENT_ACTION_OFF])
    self.assertEqual(s.subscriptions,
                     {'listen_to': {EVENT_ACTION_OFF: ['subscriber1', 'subscriber2'], EVENT_ACTION_ON: ['subscriber2']}})

    subscribers = s.get_subscribers('listen_to', event_action=[EVENT_ACTION_ON])
    self.assertEqual(subscribers, ['subscriber2'])

    subscribers = s.get_subscribers('listen_to', event_action=[EVENT_ACTION_OFF])
    self.assertListEqual(sorted(subscribers), ['subscriber1', 'subscriber2'])

    subscribers = s.get_subscribers('listen_to', event_action=[EVENT_ACTION_ON])
    self.assertListEqual(sorted(subscribers), ['subscriber2'])

    s.add_subscriber('subscriber3', 'listen_to')
    subscribers = s.get_subscribers('listen_to', event_action=[EVENT_ACTION_ON])
    self.assertListEqual(sorted(subscribers), ['subscriber2', 'subscriber3'])

    subscribers = s.get_subscribers('listen_to', event_action=[EVENT_ACTION_OFF])
    self.assertListEqual(sorted(subscribers), ['subscriber1', 'subscriber2', 'subscriber3'])

  def test_change_parent_id(self):
    s = Subscriptions()
    s.add_subscriber('subscriber', 'listen_to', event_action=[EVENT_ACTION_ON, EVENT_ACTION_OFF])
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_OFF: ['subscriber'], EVENT_ACTION_ON: ['subscriber']}})

    c = s.change_subscriber_parent_id('listen_to', 'new_listen_to')
    self.assertTrue(c)
    self.assertEqual(s.subscriptions,
                     {'new_listen_to': {EVENT_ACTION_OFF: ['subscriber'], EVENT_ACTION_ON: ['subscriber']}})

    c = s.change_subscriber_parent_id('listen_to', 'new_listen_to')
    self.assertFalse(c)

    self.assertEqual(s.subscriptions,
                     {'new_listen_to': {EVENT_ACTION_OFF: ['subscriber'], EVENT_ACTION_ON: ['subscriber']}})

  def test_change_subscriber_id(self):
    s = Subscriptions()
    s.add_subscriber('subscriber', 'listen_to', event_action=[EVENT_ACTION_ON, EVENT_ACTION_OFF])
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_OFF: ['subscriber'], EVENT_ACTION_ON: ['subscriber']}})

    c = s.change_subscriber_id('subscriber', 'new_subscriber')
    self.assertTrue(c)
    self.assertEqual(s.subscriptions, {'listen_to': {EVENT_ACTION_OFF: ['new_subscriber'], EVENT_ACTION_ON: ['new_subscriber']}})
