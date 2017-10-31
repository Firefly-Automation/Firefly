from typing import List, TypeVar

from Firefly import logging
from Firefly.const import EVENT_ACTION_ANY, EVENT_ACTON_TYPE, SOURCE_LOCATION, SOURCE_TRIGGER, TIME
from Firefly.helpers.events import Event
from Firefly.helpers.subscribers import verify_event_action, verify_event_action_time

"""
An individual trigger should be a dict type. Each individual trigger will be treated as an 'OR' trigger. Meaning
Trigger A 'OR' Trigger B.

You can have a conditional trigger by supplying a list of triggers: [ Trigger A, Trigger B ] In this case all
triggers except for at most 1 trigger must have a request and value passed into the trigger. In this case it will
treat each trigger as an 'AND' case by verifying that the return value for each request matches the value supplied.

These can be combined together like so:

[
  [ BOB: IS_PRESENT, ALICE: IS_PRESENT, LOCATION: DAWN]
]

^^ This example would require that bob and alice are both present when dawn is triggered.

[
  LOCATION: DAWN,
  [ BOB: IS_PRESENT, ALICE: IS_PRESENT, FRONT_DOOR: STATE_OPEN],
  BACK_DOOR: STATE_OPEN
]

^^ This trigger would be:

  a) Location is Dawn.
OR
  b) Back door opened.
OR
  c) Front door opened while alice and bob are present.
OR
  d) alice becomes present while bob is present and the front door is open.
OR
  e) bob becomes present while alice is present ans the front door is open.

Triggers should be formatted like so:

{
'device_id':     <DEVICE ID>,
'action_listen': [<SUBSCRIBE ACTIONS>],
'request':       <REQUEST PARAM>,                           (optional)
'value':         [<REQUEST RETURN SHOULD MATCH IN LIST]     (optional)
}


Example Trigger:
  {'device_id': 'Zach Presence', 'action_listen': [ACTION_PRESENT], 'request': PRESENCE, 'value': [IS_PRESENT] }


"""

# TODO: Change listen_id to trigger_source
# TODO: Change source to subscriber_id (This may get moved to TriggerList as a TriggerList is all for the same subscriber)
SIMPLE_TRIGGER = 'simple'
LOCATION_TRIGGER = 'location'
TIME_TRIGGER = 'time'
NUMBER_COMPARE_TRIGGER = 'number'
NUMBER_COMPARE_OPERATORS = ['le', 'ge', 'lt', 'gt']


class Trigger(object):
  def __init__(self, listen_id: str, trigger_action: EVENT_ACTON_TYPE = EVENT_ACTION_ANY, source: str = SOURCE_TRIGGER):
    self.listen_id = listen_id
    if listen_id == TIME:
      self.trigger_action = verify_event_action_time(trigger_action)
    else:
      self.trigger_action = verify_event_action(trigger_action)
    self.source = source
    self.trigger_type = self.get_trigger_type()

  def get_trigger_type(self):
    """ Gets the trigger type from the data in the trigger object. This is used for checking triggers.

    Returns: string of trigger type

    """
    if self.listen_id == TIME:
      return TIME_TRIGGER
    if self.listen_id == SOURCE_LOCATION:
      return LOCATION_TRIGGER

    # COMPLEX TRIGGERS (number_compare)
    trigger_action = self.trigger_action[0]
    prop = list(trigger_action.keys())[0]
    if type(trigger_action[prop][0]) is dict:
      type_number_compare = True
      for key in trigger_action[prop][0].keys():
        if key not in NUMBER_COMPARE_OPERATORS:
          type_number_compare = False

      if type_number_compare:
        return NUMBER_COMPARE_TRIGGER
    return SIMPLE_TRIGGER

  def check_trigger(self, firefly, event: Event, ignore_event: bool = False, **kwargs) -> bool:
    if self.trigger_type == TIME_TRIGGER:
      return self.check_time_trigger(event)

    if self.trigger_type == LOCATION_TRIGGER:
      return self.check_location_trigger(event)

    if self.trigger_type == NUMBER_COMPARE_TRIGGER and not ignore_event:
      (item, value), = event.event_action.items()
      return self.check_number_compare_trigger(item, value)

    trigger_action = self.trigger_action[0]

    if self.listen_id == event.source and not ignore_event:
      if EVENT_ACTION_ANY in trigger_action:
        return True
      for item, value in event.event_action.items():
        if item in trigger_action and value in trigger_action[item]:
          return True
        if item in trigger_action and EVENT_ACTION_ANY in trigger_action[item]:
          return True
      return False

    current_states = firefly.current_state

    if self.trigger_type == NUMBER_COMPARE_TRIGGER and ignore_event:
      prop = list(trigger_action.keys())[0]
      return self.check_number_compare_trigger(prop, current_states[self.listen_id][prop])

    try:
      prop = list(trigger_action.keys())[0]
      if current_states[self.listen_id][prop] in trigger_action[prop]:
        return True
      if EVENT_ACTION_ANY in trigger_action[prop]:
        return True
    except:
      return False

    return False

  def check_number_compare_trigger(self, event_prop, event_value) -> bool:
    logging.info('checking number trigger: %s' % self.trigger_action)
    number_compares = self.trigger_action[0][event_prop]
    valid_trigger = True
    for number_compare in number_compares:
      (operator, value), = number_compare.items()
      if operator == 'gt' and event_value > value:
        valid_trigger &= True
      elif operator == 'ge' and event_value >= value:
        valid_trigger &= True
      elif operator == 'lt' and event_value < value:
        valid_trigger &= True
      elif operator == 'le' and event_value <= value:
        valid_trigger &= True
      elif operator == 'eq' and event_value == value:
        valid_trigger &= True
      else:
        return False
    return valid_trigger

  def check_time_trigger(self, event: Event) -> bool:
    # If the event source is not time then it cant match any.
    if event.source != TIME:
      return False
    # If any time trigger in list of times matches return True.
    for t in self.trigger_action:
      if t.get('day'):
        if event.event_action['day'] != t['day']:
          continue
      if t.get('month'):
        if event.event_action['month'] != t['month']:
          continue
      if event.event_action['hour'] == t['hour'] and event.event_action['minute'] == t['minute'] and event.event_action['weekday'] in t['weekdays']:
        return True
    return False

  def check_location_trigger(self, event: Event) -> bool:
    if event.source != SOURCE_LOCATION:
      return False

    for t in self.trigger_action:
      if SOURCE_LOCATION not in event.event_action:
        return False
      if SOURCE_LOCATION not in t:
        return False
      for day_event in t.get(SOURCE_LOCATION):
        if day_event == event.event_action.get(SOURCE_LOCATION):
          return True
    return False

  def __str__(self):
    return '<FIREFLY TRIGGER - LISTEN TO: %s | TRIGGER ACTION: %s >' % (self.listen_id, self.trigger_action)

  def __repr__(self):
    return str(self.__dict__)

  def __hash__(self):
    return hash(str(self.__dict__))

  def __eq__(self, other):
    if type(other) is not dict:
      return self.__dict__ == other.__dict__
    else:
      return self.__dict__ == other

  def export(self):
    return {
      'listen_id':      self.listen_id,
      'trigger_action': self.trigger_action,
      'source':         self.source
    }


TriggerType = TypeVar('TriggerType', Trigger, List[Trigger])

"""
TriggerSet is a list of triggers that are &&'ed together when checking. 

A single trigger in a TriggerSet will return False when checking. 

Example: 
trigger_set = [{A:Open},{B:Close}]
event_action = {A:Open}
current state of B = Open

trigger_set.check_triggers(event) should return False
"""


class TriggerSet(object):
  def __init__(self, firefly, subscriber_id, trigger_set=[], **kwargs):
    self.firefly = firefly
    self.subscriber_id = subscriber_id
    self.trigger_set = []
    self.trigger_sources = set()
    if trigger_set:
      self.import_trigger_set(trigger_set)

  def check_triggers(self, event: Event, ignore_event: bool = False, **kwargs) -> bool:
    # Event source is not in TriggerSet sources -> return False.
    if event.source not in self.trigger_sources and not ignore_event:
      return False
    for trigger in self.trigger_set:
      if not trigger.check_trigger(self.firefly, event, ignore_event, **kwargs):
        return False
    return True

  def add_trigger(self, trigger: Trigger):
    if trigger in self.trigger_set:
      return False

    if {trigger} in [{t} for t in self.trigger_set]:
      logging.info('Trigger already in triggers: %s' % trigger)
      return False

    self.trigger_sources.add(trigger.listen_id)
    self.trigger_set.append(trigger)
    if self.check_for_number_compare(trigger.trigger_action):
      return self.add_number_compare_trigger(trigger)
    if trigger.listen_id != TIME:
      logging.debug('Adding subscription: %s %s %s' % (self.subscriber_id, trigger.listen_id, trigger.trigger_action))
      self.firefly.subscriptions.add_subscriber(self.subscriber_id, trigger.listen_id, trigger.trigger_action)
    else:
      self.firefly.subscriptions.add_subscriber(self.subscriber_id, trigger.listen_id, EVENT_ACTION_ANY)
    return True

  def export(self, **kwargs):
    return [trigger.export() for trigger in self.trigger_set]

  def import_trigger_set(self, trigger_set, **kwargs):
    for trigger in trigger_set:
      self.add_trigger(trigger)

  def add_number_compare_trigger(self, trigger):
    logging.debug('adding number compare trigger: %s' % trigger)
    try:
      (trigger_prop, trigger_value), = trigger.trigger_action[0].items()
    except:
      logging.error('too many triggers in number compare trigger')
      return False

    self.firefly.subscriptions.add_subscriber(self.subscriber_id, trigger.listen_id, {
      trigger_prop: EVENT_ACTION_ANY
    })
    return True

  def check_for_number_compare(self, trigger_action):
    for action in trigger_action:
      for trigger_prop, trigger_values in action.items():
        if type(trigger_values) is not list:
          return False
        for trigger_value in trigger_values:
          if type(trigger_value) is not dict:
            return False
          for action_key in trigger_value.keys():
            if action_key not in ['lt', 'gt', 'le', 'ge']:
              return False
    return True


"""
TriggerList is a list of TriggerSet(s) that are ||'ed together when checking.

A single TriggerSet returning True when checking triggers should return True.

Example:
trigger_set_a = [{A:Open},{B:Close}]
trigger_set_b = [{A:Open},{C:Close}]
event_action = {A:Open}
Current state of B = Open
Current state of C = Close

trigger_list = [trigger_set_a, trigger_set_b]
trigger_list.check_triggers(event) should return True
"""


# TODO: Base TriggerList off of the format of Triggers below.
class TriggerList(object):
  def __init__(self, firefly, subscriber_id, **kwargs):
    self.firefly = firefly
    self.subscriber_id = subscriber_id
    self.trigger_list = []
    self.trigger_sources = set()

  def check_triggers(self, event: Event, ignore_event: bool = False, **kwargs) -> bool:
    for trigger_set in self.trigger_list:
      if trigger_set.check_triggers(event, ignore_event, **kwargs):
        return True
    return False

  def add_trigger_set(self, trigger_set: TriggerSet) -> bool:
    if trigger_set in self.trigger_list:
      return False

    self.trigger_list.append(trigger_set)
    self.trigger_sources.update(trigger_set.trigger_sources)
    return True

  def export(self, **kwargs):
    return [trigger_set.export() for trigger_set in self.trigger_list]

  def import_trigger_list(self, trigger_list, **kwargs):
    for trigger_set in trigger_list:
      self.add_trigger_set(TriggerSet(self.firefly, self.subscriber_id, trigger_set))


class Triggers(TriggerList):
  def __init__(self, firefly, source_id):
    super().__init__(firefly, source_id)

  def add_trigger(self, trigger) -> bool:
    if type(trigger) is not list:
      trigger = [trigger]
    if set(trigger) in [set(t.trigger_set) for t in self.trigger_list]:
      logging.info('Trigger already in trigger_set: %s' % trigger)
      return False
    return self.add_trigger_set(TriggerSet(self.firefly, self.subscriber_id, trigger))

  def import_triggers(self, import_data: list) -> int:
    import_count = 0
    for trigger in import_data:
      triggers = []
      for t in trigger:
        triggers.append(Trigger(**t))
      import_count += 1 if self.add_trigger(triggers) else 0
    return import_count

  # TODO: Add functions to remove triggers. Is this really needed?
  def remove_triggers(self, trigger):
    pass

  @property
  def triggers(self):
    return self.export()
