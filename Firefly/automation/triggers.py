from Firefly import logging
from Firefly.helpers.events import Request, Event
from Firefly.const import SOURCE_TRIGGER, EVENT_ACTION_ANY, EVENT_ACTON_TYPE, TIME, SOURCE_LOCATION
from Firefly.helpers.subscribers import verify_event_action, verify_event_action_time
import asyncio
from typing import TypeVar, List

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


class Trigger(object):
  def __init__(self, listen_id: str, event_action: EVENT_ACTON_TYPE = EVENT_ACTION_ANY, source: str = SOURCE_TRIGGER):
    self._listen_id = listen_id
    if listen_id == TIME:
      self._listen_action = verify_event_action_time(event_action)
    else:
      self._listen_action = verify_event_action(event_action)
    self._source = source

   # TODO: Build this out.
  def check_trigger(self, event: Event, ignore_event: bool = False, **kwargs) -> bool:
    # TODO: checks for location and time triggers
    # TODO: Trigger source in Event?
    # TODO: Check states of other trigger devices using firefly.current_state (need to have firefly in Trigger or pass in current states or firefly when called.
    return False

  def __str__(self):
    return '<FIREFLY TRIGGER - LISTEN TO: %s | LISTEN ACTION: %s >' % (self.listen_id, self.listen_action)

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
      'listen_id':    self.listen_id,
      'event_action': self.listen_action,
      'source':       self.source
    }

  @property
  def listen_id(self):
    return self._listen_id

  @property
  def listen_action(self):
    return self._listen_action

  @property
  def source(self):
    return self._source


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
  def __init__(self, **kwargs):
    self.trigger_set = []
    #if kwargs.get('trigger_set'):
    #  self.import_trigger_set(kwargs.get('trigger_set'))

  def check_triggers(self, event: Event, ignore_event: bool = False, **kwargs) -> bool:
    for trigger in self.trigger_set:
      if not trigger.check_trigger(event, ignore_event, **kwargs):
        return False
    return True

  def add_trigger(self, trigger):
    # Need to make sure that trigger set is not already in trigger set
    # self.trigger_set.append(trigger)
    pass

  def export(self, **kwargs):
    pass

  def import_trigger_set(self, trigger_set, **kwargs):
    pass

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
class TriggerList(object):
  def __init__(self, **kwargs):
    self.trigger_list = []

  def check_triggers(self, event: Event, ignore_event: bool = False, **kwargs) -> bool:
    for trigger_set in self.trigger_list:
      if trigger_set.check_triggers(event, ignore_event, **kwargs):
        return True
    return False

  def add_trigger_set(self, trigger_set):
    # Need to make sure that trigger set is not already in trigger list
    # self.trigger_list.append(trigger_set)
    pass

  def export(self, **kwargs):
    pass

  def import_trigger_list(self, **kwargs):
    # for trigger_set in trigger_list:
    #   self.add_trigger_set(TriggerSet(trigger_set=trigger_set))
    pass


# TODO: Triggers should wrap TriggerSet. This will make it easier to use in future code beacuse we think in triggers like:
'''
class Triggers(TriggerSet):
  def __init__(self, firefly, soruce_id):
     super().__init__(firefly, source_id)
'''
class Triggers(object):
  def __init__(self, firefly, source_id):
    """
    Args:
      firefly (firefly): Firefly object
      source_id (str): The source of the triggers object. This is used to build out the subscribers list.
    """
    self._firefly = firefly
    self._source_id = source_id
    self._triggers = []
    self._trigger_sources = set()

  def add_trigger(self, trigger: TriggerType) -> bool:
    logging.info('Adding trigger: %s' % trigger)

    if type(trigger) is not list:
      trigger = [trigger]

    if set(trigger) in [set(t) for t in self.triggers]:
      logging.info('Trigger already in triggers: %s' % trigger)
      return False

    self.triggers.append(trigger)

    for t in trigger:
      if t.listen_id != TIME:
        logging.debug('Adding subscription: %s %s %s' % (self._source_id, t.listen_id, t.listen_action))
        self._firefly.subscriptions.add_subscriber(self._source_id, t.listen_id, t.listen_action)
        self._trigger_sources.add(t.listen_id)
      else:
        self._firefly.subscriptions.add_subscriber(self._source_id, t.listen_id, EVENT_ACTION_ANY)
        self._trigger_sources.add(t.listen_id)
    return True

  def remove_trigger(self, trigger: TriggerType) -> bool:
    logging.info('Removing trigger: %s' % trigger)

    if type(trigger) is not list:
      trigger = [trigger]

    if trigger not in self.triggers:
      logging.info('trigger not in triggers. Can not remove.')
      return False

    try:
      # Remove trigger from triggers
      self.triggers.remove(trigger)
      # Delete all subscriptions from trigger source
      self._firefly.subscriptions.delete_all_subscriptions(self._source_id)
      self._trigger_sources = set()
      # Add all triggers back in
      for trigs in self.triggers:
        for t in trigs:
          self._firefly.subscriptions.add_subscriber(self._source_id, t.listen_id, t.listen_action)
          self._trigger_sources.add(t.listen_id)
    except:
      logging.error(code='FF.TRI.REM.001', args=(trigger))  # unknown error removing trigger: %s
      return False

    return True

  def export(self):
    logging.info('Exporting triggers')
    export_data = []

    for trigger in self.triggers:
      trigger_section = []
      for t in trigger:
        trigger_section.append(t.export())
      export_data.append(trigger_section)

    return export_data

  def import_triggers(self, import_data: list) -> int:
    import_count = 0
    for trigger in import_data:
      triggers = []
      for t in trigger:
        triggers.append(Trigger(**t))
      import_count += 1 if self.add_trigger(triggers) else 0

    for trigs in self.triggers:
      for t in trigs:
        if t.listen_id != TIME:
          logging.debug('Adding subscription: %s %s %s' % (self._source_id, t.listen_id, t.listen_action))
          self._firefly.subscriptions.add_subscriber(self._source_id, t.listen_id, t.listen_action)
          self._trigger_sources.add(t.listen_id)
        else:
          self._firefly.subscriptions.add_subscriber(self._source_id, t.listen_id, EVENT_ACTION_ANY)
          self._trigger_sources.add(t.listen_id)

    return import_count

  def check_triggers(self, event: Event, ignore_event: bool = False, **kwargs) -> bool:
    """
    Validates that an event relates to the triggers. Should be called when an event is received.

    Args:
      ignore_event (bool): Ignore the device_id and action_type from the event and just see if trigger conditions are
                           met.
      **kwargs ():
    """

    devices = self.trigger_sources
    # current_states = self._firefly.get_device_states(devices.copy())

    current_states = self._firefly.current_state

    if event.source not in devices and not ignore_event:
      return False

    for triggers in self.triggers:
      trigger_valid = True
      event_valid = False
      trigger_devices = [trigger.listen_id for trigger in triggers]
      if event.source not in trigger_devices:
        continue
      for trigger in triggers:
        listen_action = trigger.listen_action[0]  # events are a list always containing a single dict
        trigger_source = trigger.listen_id

        if trigger_source == TIME:
          trigger_valid &= self.check_time_trigger(event, trigger)
          event_valid = True
          continue
        if trigger_source == SOURCE_LOCATION:
          trigger_valid &= self.check_location_trigger(event, trigger)
          event_valid = True
          continue
        if EVENT_ACTION_ANY in listen_action:  # if EVENT_ACTION_ANY is a property
          trigger_valid = True
          event_valid = True
          continue

        for prop, vals in listen_action.items():
          try:
            # If ANY then continue
            if EVENT_ACTION_ANY in vals:
              trigger_valid = True
              if prop in event.event_action:
                event_valid = True
              continue
            # If the trigger value is in the event, use the event value unless ignore event.
            if prop in event.event_action and event.source == trigger_source and not ignore_event:
              if event.event_action[prop] in vals:
                trigger_valid = True
                event_valid = True
                continue
              else:
                trigger_valid = False
                break
            else:
              if current_states[trigger_source][prop] in vals:
                trigger_valid = True
                continue
              else:
                trigger_valid = False
                break
          except:
            logging.error(code='FF.TRI.CHE.001')  # cant find device or property in current status
            trigger_valid = False
          if not trigger_valid:
            break

      if trigger_valid:
        if ignore_event:
          return True
        return trigger_valid & event_valid

    return False

  def check_time_trigger(self, event: Event, trigger: Trigger) -> bool:
    # If the event source is not time then it cant match any.
    if event.source != TIME:
      return False
    # If any time trigger in list of times matches return True.
    for t in trigger.listen_action:
      if t.get('day'):
        if event.event_action['day'] != t['day']:
          continue
      if t.get('month'):
        if event.event_action['month'] != t['month']:
          continue
      if event.event_action['hour'] == t['hour'] and event.event_action['minute'] == t['minute'] and event.event_action[
        'weekday'] in t['weekdays']:
        return True

    return False

  def check_location_trigger(self, event: Event, trigger: Trigger) -> bool:
    if event.source != SOURCE_LOCATION:
      return False

    for t in trigger.listen_action:
      if SOURCE_LOCATION not in event.event_action:
        return False
      if SOURCE_LOCATION not in t:
        return False
      for day_event in t.get(SOURCE_LOCATION):
        if day_event == event.event_action.get(SOURCE_LOCATION):
          return True

    return False

  @property
  def triggers(self):
    return self._triggers

  @property
  def trigger_sources(self):
    return self._trigger_sources
