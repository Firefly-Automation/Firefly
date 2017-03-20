from Firefly import logging
from Firefly.automation.triggers import Trigger, Triggers
from Firefly.const import TYPE_AUTOMATION
import asyncio
from Firefly import aliases
import uuid
from Firefly.helpers.events import Command

from typing import Callable

# TODO: move this to automation
from Firefly.util.conditions import check_conditions

class Automation(object):
  def __init__(self, firefly, package, title, author, event_handler, **kwargs):
    ff_id = kwargs.get('ff_id')
    alias = kwargs.get('alias')

    self._firefly = firefly
    self._package = package
    self._author = author
    self._title = title
    self._conditions = kwargs.get('conditions') if kwargs.get('conditions') else {}
    self._commands = kwargs.get('commands') if kwargs.get('commands') else []
    self._event_handler = event_handler
    self._initial_values = kwargs.get('initial_values')
    self._command_mapping = {}


    # If alias given but no ID look at config files for ID.
    if not ff_id and alias:
      if aliases.get_device_id(alias):
        device_id = aliases.get_device_id(alias)

    elif ff_id and not alias:
      if aliases.get_alias(ff_id):
        alias = aliases.get_alias(ff_id)

    # If no ff_id ID given -> generate random ID.
    if not ff_id:
      device_id = str(uuid.uuid4())

    self._id = ff_id
    self._alias = alias if alias else ff_id
    aliases.set_alias(self._id, self._alias)

    self._triggers = Triggers(firefly, ff_id)

    triggers = kwargs.get('triggers')
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

  @asyncio.coroutine
  def event(self, event, **kwargs):
    logging.info('[AUTOMATION] %s - Receiving event: %s' % (self.id, event))
    valid = True
    valid &= check_conditions(self._firefly, self.conditions)
    # TODO: If i have issues change this to valid &= yield from and fix in triggers.py....
    valid &= yield from self.triggers.check_triggers(event)
    if valid:
      return self.get_event_handler(event, **kwargs)



  # TODO: export automation
  # TODO import automation
  def export(self, **kwargs):
    export_data = {
      'type': self.type,
      'package': self._package,
      'ff_id': self.id,
      'conditions': self.conditions,
      'triggers': self.triggers.export(),
      'initial_values': 'TODO INITIAL VALUES'
    }
    return export_data

  def add_command(self, command: str, function: Callable) -> None:
    """
    Adds a command to the list of supported ff_id commands.

    Args:
      command (str): The string of the command
      function (Callable): The function to be executed.
    """
    self._command_mapping[command] = function

  def command(self, command, **kwargs):
    if command.command in self.command_map.keys():
      return self.command_map[command.command](**command.args)

  @property
  def command_map(self):
    return self._command_mapping

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
  def get_event_handler(self):
    return self._event_handler

  @property
  def type(self):
    return TYPE_AUTOMATION