from Firefly import logging
from Firefly.const import (EVENT_ACTION_ANY, EVENT_ACTON_TYPE, TIME)
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

  def get_subscribers(self, subscribe_to_id: str, event_action: dict = {EVENT_ACTION_ANY:EVENT_ACTION_ANY}) -> List[str]:
    """Gets a list of subscribers.

    Returns a list subscriber IDs that are subscribed to the ff_id passed in for the event types that are pass and any
    subscriber that is listening to the EVENT_ACTION_ANY.

    Args:
      subscribe_to_id (str): subscriber ID
      event_action (list): list of event types to listen for

    Returns:
      list: List of subscriber IDs
    """

    _event_action = event_action.copy()
    _event_action = verify_event_action(_event_action, get_subscribers=True)

    try:
      subscriptions = self.subscriptions[subscribe_to_id]
    except KeyError:
      logging.warn('Component (%s) not found in subscriptions' % subscribe_to_id)
      return []

    # Get subscribers listening to Anything
    try:
      subscribers_any = set(subscriptions[EVENT_ACTION_ANY][EVENT_ACTION_ANY])
    except:
      subscribers_any = set()

    subscribers_prop_any = set()
    subscribers = set()

    for ea in _event_action:
      if type(ea) is not dict:
        logging.error('[get_subscribers] Event action is not type dict: %s [ERROR CODE: SUB.DEL.11]' % str(ea))
        continue

      for prop, act in ea.items():
        # Get any subscribers listening for any of that prop
        try:
          subscribers_prop_any.update(subscriptions[prop][EVENT_ACTION_ANY])
        except:
          pass

        # Get subscribers for the prop and action
        for a in act:
          try:
            subscribers.update(subscriptions[prop][a])
          except:
            pass

    subscribers.update(subscribers_any, subscribers_prop_any)
    return list(subscribers)

  def add_subscriber(self, subscriber_id: str, subscribe_to_id: str,
                     event_action: EVENT_ACTON_TYPE = EVENT_ACTION_ANY) -> None:
    """Add a subscriber.

    This adds a new subscriber.

    Args:
      subscriber_id (str): subscriber id.
      subscribe_to_id (str): id of ff_id listening to.
      event_action (dict): The event types to listen to.
    """

    event_action = verify_event_action(event_action)

    if subscribe_to_id not in self.subscriptions:
      logging.info('%s not in subscriptions. Adding new subscription.' % subscribe_to_id)
      self.subscriptions[subscribe_to_id] = {}
    subscriptions = self.subscriptions[subscribe_to_id]

    for ea in event_action:
      # Deal with EVENT_ACTION_ANY.
      if type(ea) is str:
        if ea == EVENT_ACTION_ANY:
          if EVENT_ACTION_ANY not in subscriptions:
            subscriptions[EVENT_ACTION_ANY] = {}
          if event_action[ea] not in subscriptions[EVENT_ACTION_ANY]:
            subscriptions[EVENT_ACTION_ANY][event_action[ea]] = []
          if subscriber_id not in subscriptions[EVENT_ACTION_ANY][event_action[ea]]:
            subscriptions[EVENT_ACTION_ANY][event_action[ea]].append(subscriber_id)

        else:
          logging.warn('Got string to event_action making it {%s : ANY}' % event_action)
          event_action = {event_action: EVENT_ACTION_ANY}

      # Deal with a dict of event actions.
      if type(ea) is dict:
        for evt, act in ea.items():
          if evt not in subscriptions:
            subscriptions[evt] = {}
          if type(act) is list:
            for a in act:
              if a not in subscriptions[evt].keys():
                subscriptions[evt][a] = []
              if subscriber_id not in subscriptions[evt][a]:
                subscriptions[evt][a].append(subscriber_id)
          else:
            if act not in subscriptions[evt].keys():
              subscriptions[evt][act] = []
            if subscriber_id not in subscriptions[evt][act]:
              subscriptions[evt][act].append(subscriber_id)

  def get_all_subscribers(self, subscribe_to_id: str) -> list:
    """Get a list of all subscribers to a component.

    Args:
      subscribe_to_id (str): The component id.

    Returns: A list of subscriber IDs

    """
    try:
      subscriptions = self.subscriptions[subscribe_to_id]
    except KeyError:
      logging.warn('Component (%s) not found in subscriptions' % subscribe_to_id)
      return []

    subscribers = set()

    for act, itm in subscriptions.items():
      if type(itm) is list:
        subscribers.update(itm)
      if type(itm) is dict:
        for itm_prop, itm_act in itm.items():
          if type(itm_act) is list:
            subscribers.update(itm_act)
          else:
            logging.error('[get_all_subscribers] unknown error [ERROR CODE: SUB.DEL.7]')

    return list(subscribers)

  def get_subscriber_items(self, subscriber_id: str, subscribe_to_id: str) -> dict:
    """Get a dict of subscriber items.

    Args:
      subscriber_id (str): The subscriber ID to be deleted
      subscribe_to_id (str): The is that the subscriber is listening to

    Returns: A dict of subscriber items.

    """
    subscription_items = {}
    try:
      subscriptions = self.subscriptions[subscribe_to_id]
    except KeyError:
      logging.warn('Component (%s) not found in subscriptions' % subscribe_to_id)
      return {}

    for act, itm in subscriptions.items():
      if type(itm) is list:
        if subscriber_id in itm:
          subscription_items[act] = True

      if type(itm) is dict:
        for itm_act, itm_subs in itm.items():
          if type(itm_subs) is not list:
            logging.info('[get_subscriber_items] subscriber list is not list.')
            continue

          if subscriber_id in itm_subs:
            if subscription_items.get(act) is None:
              subscription_items[act] = {}
            subscription_items[act][itm_act] = True

    return subscription_items

  def delete_subscriber(self, subscriber_id: str, subscribe_to_id: str,
                        event_action: EVENT_ACTON_TYPE = EVENT_ACTION_ANY,
                        delete_all: bool = False) -> int:
    """Deletes or Replace a subscriber.

    Args:
      subscriber_id (str): The subscriber ID to be deleted
      subscribe_to_id (str): The is that the subscriber is listening to
      event_action (list): The event types to be deleted
      delete_all (bool): Delete from all event types if True

    Returns:
      (int): The number of subscriptions changed
    """

    return self.delete_replace_subscriber(subscriber_id, subscribe_to_id, event_action, delete_all)


  def delete_all_subscriptions(self, subscriber_id: str) -> int:
    """Delete all subscriptions from all devices from subscriber.
    
    Args:
      subscriber_id (str): The subscriber ID to be deleted

    Returns:
      (int): The number of subscriptions deleted

    """
    total_deletions = 0
    for sub in self.subscriptions.keys():
      total_deletions += self.delete_subscriber(subscriber_id, sub, delete_all=True)
    return total_deletions



  def delete_replace_subscriber(self, subscriber_id: str, subscribe_to_id: str,
                                event_action: EVENT_ACTON_TYPE = EVENT_ACTION_ANY,
                                change_all: bool = False, new_subscriber_id: str = None) -> int:
    """Deletes or Replace a subscriber.

    Args:
      subscriber_id (str): The subscriber ID to be deleted
      subscribe_to_id (str): The is that the subscriber is listening to
      event_action (list): The event types to be deleted
      change_all (bool): Delete from all event types if True
      new_subscriber_id (str): New subscriber ID

    Returns:
      (int): The number of subscriptions changed
    """

    changed_subscriptions = 0
    event_action = verify_event_action(event_action)

    try:
      subscriptions = self.subscriptions[subscribe_to_id]
    except KeyError:
      logging.warn('Component (%s) not found in subscriptions' % subscribe_to_id)
      return changed_subscriptions

    subscription_items = self.get_subscriber_items(subscriber_id, subscribe_to_id)

    if change_all:
      for prop, act in subscription_items.items():
        if type(act) is dict:
          for act_itm in act.keys():
            try:
              subscriptions[prop][act_itm].remove(subscriber_id)
              if new_subscriber_id is not None:
                subscriptions[prop][act_itm].append(new_subscriber_id)
              changed_subscriptions += 1
            except (KeyError, ValueError):
              logging.error(
                '[delete_subscriber] - subscriber not found in subscriptions (it should have been) [ERROR CODE: SUB.DEL.1]')
            except Exception as e:
              logging.error('[delete_subscriber] Unknown Error: %s [ERROR CODE: SUB.DEL.10]' % e)
      return changed_subscriptions

    else:
      for action in event_action:
        if action == EVENT_ACTION_ANY and EVENT_ACTION_ANY in subscription_items:
          if EVENT_ACTION_ANY in subscription_items[EVENT_ACTION_ANY]:
            try:
              subscriptions[EVENT_ACTON_TYPE][EVENT_ACTION_ANY].remove(subscriber_id)
              if new_subscriber_id is not None:
                subscriptions[EVENT_ACTON_TYPE][EVENT_ACTION_ANY].append(new_subscriber_id)
              changed_subscriptions += 1
            except (KeyError, ValueError):
              logging.error(
                '[delete_subscriber] - subscriber not found in subscriptions (it should have been) [ERROR CODE: SUB.DEL.2]')
            except Exception as e:
              logging.error('[delete_subscriber] Unknown Error: %s [ERROR CODE: SUB.DEL.5]' % e)
        if type(action) is dict:
          for act_itm, act_prop in action.items():
            if act_itm in subscription_items:
              if type(act_prop) is not list:
                logging.error('[delete_subscriber] - subscribers are not type list. [ERROR CODE: SUB.DEL.4]')
              for p in act_prop:
                try:
                  subscriptions[act_itm][p].remove(subscriber_id)
                  if new_subscriber_id is not None:
                    subscriptions[act_itm][p].append(new_subscriber_id)
                  changed_subscriptions += 1
                except (KeyError, ValueError):
                  logging.error(
                    '[delete_subscriber] - subscriber not found in subscriptions (it should have been) [ERROR CODE: SUB.DEL.3]')
                except Exception as e:
                  logging.error('[delete_subscriber] Unknown Error: %s [ERROR CODE: SUB.DEL.6]' % e)

    return changed_subscriptions

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

  def change_subscriber_id(self, subscriber_id: str, new_subscriber_id: str) -> int:
    """
    Changes the child subscriber ID.

    The parent is the one being listed to.
          [ PARENT]                           [CHILD]
    { DEVICE_SUBSCRIBED_TO: {EVENT_ACTION: [LIST_OF_SUBSCRIBERS], ...} }

    Args:
      old_id (str): Old parent ID
      new_id (str): New Parent ID

    Returns:
      (int) Number of changes
    """
    change_count = 0
    for subscription in self.subscriptions:
      change_count += self.delete_replace_subscriber(subscriber_id, subscription, change_all=True,
                                                     new_subscriber_id=new_subscriber_id)
    return change_count


def verify_event_action(event_action: EVENT_ACTON_TYPE = EVENT_ACTION_ANY, get_subscribers: bool = False) -> list:
  """Takes and event action and returns a list of event actions.

  Args:
    event_action (EVENT_ACTON_TYPE): event_action passed in

  Returns:
    list: list of event_action dict
  """

  if type(event_action) is dict:
    return [verify_event_action_dict(event_action)]

  if event_action == EVENT_ACTION_ANY:
    return [{EVENT_ACTION_ANY:[EVENT_ACTION_ANY]}]

  if type(event_action) is list:
    new_event_actions = {}
    for ea in event_action:
      # Verify when not coming from get_subscribers
      if not get_subscribers:
        if type(ea) is not dict and ea != EVENT_ACTION_ANY:
          logging.error('event_action: %s is not type dict! Making ANY listener [ERROR CODE: SUB.DEL.9]' % event_action)
          if EVENT_ACTION_ANY in new_event_actions.keys():
            new_event_actions[EVENT_ACTION_ANY].append(ea)
          else:
            new_event_actions[EVENT_ACTION_ANY] = [ea]
        elif type(ea) is dict:
          new_event_actions.update(verify_event_action_dict(ea))
        elif ea == EVENT_ACTION_ANY:
          if EVENT_ACTION_ANY in new_event_actions.keys():
            new_event_actions[EVENT_ACTION_ANY].append(EVENT_ACTION_ANY)
          else:
            new_event_actions[EVENT_ACTION_ANY] = [EVENT_ACTION_ANY]


      # Verify when coming from get_subscribers
      if get_subscribers:
        if type(ea) is not list:
          new_event_actions.update(ea)
        if type(ea) is list:
          new_event_actions.update(ea)

    return [new_event_actions]

  logging.error("EVENT ACTION NOT VERIFIED [ERROR CODE: SUB.DEL.8]")
  return event_action


def verify_event_action_dict(event_action: dict) -> dict:
  for evt, act in event_action.items():
    if type(act) is not list:
      event_action[evt] = [act]
  return event_action

def verify_event_action_time(event_action: EVENT_ACTON_TYPE) -> list:
  if type(event_action) is dict:
    event_action = [event_action]

  for ea in event_action:
    # Check for missing items
    if 'hour' not in ea.keys():
      logging.error('hour not in time action')
      ea = {}
      continue
    if 'minute' not in ea.keys():
      logging.error('minute not in time action')
      ea = {}
      continue
    if 'weekdays' not in ea.keys():
      logging.error('weekdays not in time action. Setting to everyday.')
      ea['weekdays'] = [1,2,3,4,5,6,7]

    # Verify time ranges
    if ea['hour'] < 0 or ea['hour'] > 24:
      logging.error('hour is out of range')
      ea ={}
      continue
    if ea['minute'] < 0 or ea['minute'] > 60:
      logging.error('minute is out of range')
      ea ={}
      continue
    if max(ea['weekdays']) > 7 or min(ea['weekdays']) < 1:
      logging.error('weekdays is out of range')
      ea = {}
      continue

  return event_action

