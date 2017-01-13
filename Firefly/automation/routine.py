from Firefly import logging


class Routine(object):
  def __init__(self, firefly, routine_id, **kwargs):
    self._firefly = firefly
    self._id = routine_id
    self._alias = routine_id

    self._triggers = []
    self._actions = {}
    self._conditions = {}

  def add_trigger(self, trigger, **kwargs):
    """
    Adds a trigger for the routine.

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

    Args:
      trigger ():
      **kwargs ():
    """
    # TODO: Verify Trigger. Trigger might be good to make its own module so that triggers are a class and can be verified/updated checked and used in other actions.
    if trigger not in self._triggers:
      self._triggers.append(trigger)

  def add_condition(self, condition: dict) -> None:
    """
    Adds or updates existing conditions to the routine for execution.

    Args:
      condition (dict): The conditions to be added or updated.
    """
    self._conditions.update(condition)

  def add_action(self, command, **kwargs):
    # TODO: adding actions with optional argument of order to run in. Otherwise assume that order desnt matter
    pass

  def event(self, event, **kwargs):
    pass