from Firefly.helpers import logging
from Firefly.const import (EVENT_ACTION_ANY)
from typing import List


class Subscriptions(object):
  """Subscriptions.

  Subscriptions should be stored like so:
  { DEVICE_SUBSCRIBED_TO: {EVENT_ACTION: [LIST_OF_SUBSCRIBERS], ...} }
  """

  # TODO: Add functionality to export subscriptions to json file.

  def __init__(self):
    self.subscriptions = {}
    # TODO: Add functionality to import subscriptions from json file.

  def get_subscribers(self, subscriber_id: str, event_action: List[str] = [EVENT_ACTION_ANY]) -> List[str]:
    """Gets a list of subscribers.

    Returns a list subscriber IDs that are subscribed to the device passed in for the event types that are pass and any
    subscriber that is listening to the EVENT_ACTION_ANY.

    Args:
      subscriber_id (str): subscriber ID
      event_action (list): list of event types to listen for

    Returns:
      list: List of subscriber IDs
    """
    if type(event_action) == str:
      event_action = [event_action]
    listeners = []
    if subscriber_id not in self.subscriptions:
      return listeners
    any_listeners = self.subscriptions[subscriber_id].get(EVENT_ACTION_ANY)
    if any_listeners:
      listeners.extend(any_listeners)
    if EVENT_ACTION_ANY in event_action:
      event_action.remove(EVENT_ACTION_ANY)
    for et in event_action:
      et_listeners = self.subscriptions[subscriber_id].get(et)
      if et_listeners:
        listeners.extend(et_listeners)

    listeners = list(set(listeners))
    return listeners

  def add_subscriber(self, subscriber_id: str, subscribe_to_id: str, event_action: List[str] = [EVENT_ACTION_ANY]) -> None:
    """Add a subscriber.

    This is a new subscriber.

    Args:
      subscriber_id (str): subscriber id.
      subscribe_to_id (str): id of device listening to.
      event_action (list): The event types to listen to.
    """
    if type(event_action) == str:
      event_action = [event_action]

    if subscribe_to_id not in self.subscriptions:
      self.subscriptions[subscribe_to_id] = {}
    subscriptions = self.subscriptions[subscribe_to_id]
    for et in event_action:
      if et not in subscriptions:
        subscriptions[et] = []
      if subscriber_id not in subscriptions[et]:
        subscriptions[et].append(subscriber_id)

  def delete_subscriber(self, subscriber_id: str, subscribe_to_id: str, event_action: List[str] = [EVENT_ACTION_ANY],
                        all: bool = False) -> int:
    """Deletes a subscriber.

    Args:
      subscriber_id (str): The subscriber ID to be deleted
      subscribe_to_id (str): The is that the subscriber is listening to
      event_action (list): The event types to be deleted
      all (bool): Delete from all event types if True

    Returns:
      (int): The number of subscriptions deleted
    """
    if type(event_action) == str:
      event_action = [event_action]

    deleted_subscriptions = 0
    if subscribe_to_id not in self.subscriptions:
      return 0
    subscriptions = self.subscriptions[subscribe_to_id]

    if all:
      for et in subscriptions:
        if subscriber_id in subscriptions[et]:
          subscriptions[et].remove(subscriber_id)
          deleted_subscriptions += 1

    for et in event_action:
      if et in subscriptions:
        subscriptions[et].remove(subscriber_id)
        deleted_subscriptions += 1

    return deleted_subscriptions

  def change_subscriber_parent_id(self, old_id: str, new_id: str) -> bool:
    """
    Changes the parent subscriber ID.

    The parent is the one being listed to.
          [ PARENT]                           [CHILD]
    { DEVICE_SUBSCRIBED_TO: {EVENT_ACTION: [LIST_OF_SUBSCRIBERS], ...} }

    Args:
      old_id (str): Old parent ID
      new_id (str): New Parent ID

    Returns:
      (bool) Action successful
    """
    if old_id not in self.subscriptions:
      return False
    if new_id in self.subscriptions:
      return False
    self.subscriptions[new_id] = self.subscriptions[old_id]
    del self.subscriptions[old_id]
    return True

  def change_subscriber_id(self, old_id: str, new_id: str) -> bool:
    """
    Changes the child subscriber ID.

    The parent is the one being listed to.
          [ PARENT]                           [CHILD]
    { DEVICE_SUBSCRIBED_TO: {EVENT_ACTION: [LIST_OF_SUBSCRIBERS], ...} }

    Args:
      old_id (str): Old parent ID
      new_id (str): New Parent ID

    Returns:
      (bool) Action successful
    """
    success = False

    # TODO: check if new_id is already in list. If so return False

    for parent in self.subscriptions:
      for et, listeners in self.subscriptions[parent].items():
        if old_id in listeners:
          listeners.append(new_id)
          listeners.remove(old_id)
          success = True

    return success

  def send_event(self, from_subscriber, event_action, event):
    logging.debug('Sending Event')

  def subscribe(self, device, event_actions=[EVENT_ACTION_ANY]):
    logging.debug('Subscribing to event')
