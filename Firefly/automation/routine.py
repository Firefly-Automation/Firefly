# TODO: The base of this should become package automation

from Firefly import logging
from Firefly.automation.triggers import Trigger, Triggers

# TODO: move this to automation
from Firefly.util.conditions import check_conditions


class Routine(object):
  def __init__(self, firefly, routine_id, **kwargs):
    self._firefly = firefly
    self._id = routine_id
    self._alias = routine_id

    self._triggers = Triggers(firefly, routine_id)
    self._actions = {}
    self._conditions = {}

  def add_trigger(self, trigger, **kwargs):
    # TODO: Check trigger for list, dict or Trigger and properly import it. This can be useful to exporting/importing triggers
    # TODO cont: This might be a automation export / import function that can be called from the child object
    self._triggers.add_trigger(trigger)

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
    logging.info('Routine %s got event: %s' % (self._id, event))
    valid = True
    valid &= self._triggers.check_triggers(event)
    logging.info('*** CHECK AFTER TRIGGER CHECK *** %s ' % valid)
    print(self._triggers.export())
    valid &= check_conditions(self._firefly, self._conditions)
    if valid:
      self.event_handler(event, **kwargs)

  def event_handler(self, event, **kwargs):
    logging.critical('********************* ROUTINE ******************************')