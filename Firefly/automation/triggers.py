from Firefly import logging
from Firefly.helpers.events import Request, Event
from Firefly.const import SOURCE_TRIGGER, EVENT_ACTION_ANY

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
  def __init__(self, listen_id: str, listen_action: str = '', request: str = '', request_verify: str = '',
               source: str = SOURCE_TRIGGER):
    self._listen_id = listen_id
    self._listen_action = listen_action if listen_action else EVENT_ACTION_ANY
    self._request = request
    self._value = request_verify
    self._source = source

  def __str__(self):
    return '<FIREFLY TRIGGER - LISTEN TO: %s | LISTEN ACTION: %s >' % (self.listen_id, self.listen_action)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def export(self):
    return {
      'listen_id':      self.listen_id,
      'listen_action':  self.listen_action,
      'request':        self.request_property,
      'request_verify': self.request_verify,
      'source':         self.source
    }

  @property
  def listen_id(self):
    return self._listen_id

  @property
  def listen_action(self):
    return self._listen_action

  @property
  def request_property(self):
    return self._request

  @property
  def request_verify(self):
    return self._value

  @property
  def source(self):
    return self._source

  @property
  def request(self):
    return Request(self.listen_id, self.source, self.request_property)


TriggerType = TypeVar('TriggerType', Trigger, List[Trigger])


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

  def add_trigger(self, trigger: TriggerType) -> bool:
    logging.info('Adding trigger: %s' % trigger)
    if type(trigger) == Trigger:
      if trigger in self.triggers:
        logging.error('Trigger already in triggers: %s' % trigger)
        return False

    # TODO: See if this can be cleaned up
    if type(trigger) == list:
      # set existing to false until we know that there is a list
      existing = False
      # set to true before iterating through list just so its assigned.
      existing_trig = True
      # Go though all triggers.
      for trig in self.triggers:
        # See if trigger is list.
        if type(trig) == list:
          # If list, set existing and existing_trig to True.
          existing = True
          existing_trig = True
          # For each trigger in the list, see if that trigger is in the new list of triggers. || that. If all triggers
          # match then it should return true.
          for t in trig:
            existing_trig &= t in trigger
        # Or the results of that with the existing results.
        existing &= existing_trig
        if existing:
          logging.error('Trigger already in triggers %s' % trigger)
          return False

    self.triggers.append(trigger)
    # Add subscribers.
    # If single trigger then just add that subscriber.
    if type(trigger) == Trigger:
      logging.debug('Adding subscription: %s %s %s' % (self._source_id, trigger.listen_id, trigger.listen_action))
      self._firefly.subscriptions.add_subscriber(self._source_id, trigger.listen_id, trigger.listen_action)
      return True
    # If a list of triggers that add the subscribers for each trigger.
    if type(trigger) == list:
      for t in trigger:
        logging.debug('Adding subscription: %s %s %s' % (self._source_id, t.listen_id, t.listen_action))
        self._firefly.subscriptions.add_subscriber(self._source_id, t.listen_id, t.listen_action)
      return True

    return False

  def remove_trigger(self, trigger: TriggerType) -> bool:
    logging.info('Removing trigger: %s' % trigger)
    if type(trigger) == Trigger:
      if trigger not in self.triggers:
        logging.error('Trigger not in triggers: %s' % trigger)
        return False
      self.triggers.remove(trigger)
      return True

    # TODO: See if this can be cleaned up
    if type(trigger) == list:
      # set existing to false until we know that there is a list
      existing = False
      # set to true before iterating through list just so its assigned.
      existing_trig = True
      # Go though all triggers.
      index = 0
      for trig in self.triggers:
        # See if trigger is list.
        if type(trig) == list:
          # If list, set existing and existing_trig to True.
          existing = True
          existing_trig = True
          # For each trigger in the list, see if that trigger is in the new list of triggers. || that. If all triggers
          # match then it should return true.
          for t in trig:
            existing_trig &= t in trigger
        # Or the results of that with the existing results.
        existing &= existing_trig
        if existing:
          logging.error('Trigger not  in triggers %s' % trigger)
          self.triggers.pop(index)
          return True
        index += 1
    return False

  def export(self):
    logging.info('Exporting triggers')
    export_data = []

    for trigger in self.triggers:
      if type(trigger) == Trigger:
        export_data.append(trigger.export())

      if type(trigger) == list:
        trigger_section = []
        for t in trigger:
          trigger_section.append(t.export())
        export_data.append(trigger_section)

    return export_data

  def import_triggers(self, import_data: list) -> int:
    import_count = 0
    for trigger in import_data:
      if type(trigger) == dict:
        t = Trigger(**trigger)
        import_count += 1 if self.add_trigger(t) else 0

      if type(trigger) == list:
        triggers = []
        for t in trigger:
          triggers.append(Trigger(**t))
          import_count += 1 if self.add_trigger(triggers) else 0

    return import_count



  def check_triggers(self, event: Event, ignore_event: bool = False, **kwargs) -> bool:
    """
    Check triggers should be called when an event is received.

    If only matching on one trigger, then trigger_request and trigger_verify will be ignored in place of check the event
    source and event action.

    If checking against a list of triggers then requests will be made to each ff_id to see if it matched the required
    verify before returning True.

    The device_id and event_type from the event will need to match the trigger for it to return true. This can be
    overwritten by passing in ignore_event

    Args:
      ignore_event (bool): Ignore the device_id and action_type from the event and just see if trigger conditions are
                           met.
      **kwargs ():
    """
    valid = len(self.triggers) > 0
    for trigger in self.triggers:
      if type(trigger) == Trigger:
        valid = True
        valid &= (event.source == trigger.listen_id)
        valid &= (trigger.listen_action in event.event_action  or trigger.listen_action == EVENT_ACTION_ANY)

        if (trigger.request_property != '' and trigger.request_verify != '' and trigger.request_verify != EVENT_ACTION_ANY) and not ignore_event:
          response = self._firefly.send_request(trigger.request)
          valid &= response == trigger.request_verify

        # If a single trigger is valid then it should respond as true.
        if valid:
          return True

      # TODO: rewrite this... This is from hell
      if type(trigger) == list:
        for t in trigger:
          valid_t = True
          valid_event = False
          no_request_count = 0
          # If trigger is not type Trigger then it fails
          if not type(t) == Trigger:
            valid = False
          if (event.source == t.listen_id) and (trigger.listen_action in event.event_action or t.listen_action == EVENT_ACTION_ANY):
            valid_event = True
          if (t.request_property != '' and t.request_verify != '' and t.request_verify != EVENT_ACTION_ANY) and not ignore_event:
            response = self._firefly.send_request(t.request)
            valid_t &= response == t.request_verify
          elif t.request_property == '' and t.request_verify == '':
            no_request_count += 1

          if valid_t or ((no_request_count <= 1 and valid_event) or ignore_event):
            valid_t &= True
          else:
            valid_t &= False
          valid &= valid_t
        if valid:
          return True

    return False


  @property
  def triggers(self):
    return self._triggers