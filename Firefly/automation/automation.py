from Firefly import logging
from Firefly.automation.triggers import Trigger, Triggers
from Firefly.const import TYPE_AUTOMATION

# TODO: move this to automation
from Firefly.util.conditions import check_conditions

class Automation(object):
  def __init__(self, firefly, ff_id, event_handler, install_package, triggers=None, conditions={}, actions=None, initial_values={}, **kwargs):
    self._firefly = firefly
    self._id = ff_id
    self._install_package = install_package
    self._triggers = Triggers(firefly, ff_id)
    self._actions = [] # TODO: import actions if there are actions
    self._conditions = conditions
    self._event_handler = event_handler
    self._initial_values = initial_values

    if triggers:
      self.import_triggers(triggers)


  def import_triggers(self, triggers):
    logging.info('Importing triggers into %s - %s' % (self.id, triggers))
    self.triggers.import_triggers(triggers)

  def export_triggers(self):
    logging.info('Exporting triggers into %s' % self.id)
    return self.triggers.export()

  def add_condition(self, condition: dict):
    """
    Adds or updates existing conditions to the routine for execution.

    Args:
     condition (dict): The conditions to be added or updated.
    """
    self._conditions.update(condition)

  # TODO: remove condition
  # TODO: export condition?
  # TODO: import condition?

  def add_trigger(self, trigger, **kwargs):
    self.triggers.add_trigger(trigger)

  def remove_trigger(self, trigger, **kwargs):
    self.triggers.remove_trigger(trigger)

  def add_action(self, command, command_conditions={}, **kwargs):
    action = {'command': command, 'conditions': command_conditions, 'kwargs': kwargs}
    if action not in self.actions:
      self.actions.append(action)

  # TODO: remove action
  # TODO: export action
  # TODO: import action


  def event(self, event, **kwargs):
    logging.info('[AUTOMATION] %s - Receiving event: %s' % (self.id, event))
    valid = True
    valid &= check_conditions(self._firefly, self.conditions)
    valid &= self.triggers.check_triggers(event)
    if valid:
      self.event_handler(event, **kwargs)

  # TODO: export automation
  # TODO import automation
  def export(self):
    export_data = {
      'type': self.type,
      'package': self._install_package,
      'ff_id': self.id,
      'conditions': self.conditions,
      'triggers': self.triggers.export(),
      'actions': 'TODO: ACTIONS',
      'initial_values': 'TODO INITIAL VALUES'
    }
    return export_data

  @property
  def actions(self):
    return self._actions

  @property
  def triggers(self):
    return self._triggers

  @property
  def id(self):
    return self._id

  @property
  def conditions(self):
    return self._conditions

  @property
  def event_handler(self):
    return self._event_handler

  @property
  def type(self):
    return TYPE_AUTOMATION