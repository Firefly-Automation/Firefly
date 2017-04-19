from Firefly import logging
from Firefly.automation.triggers import Trigger, Triggers
from Firefly.const import TYPE_AUTOMATION, API_INFO_REQUEST
import asyncio
from Firefly import aliases
import uuid
from Firefly.helpers.events import Request
from Firefly.helpers.conditions import Conditions
from Firefly.helpers.action import Action

from typing import Callable, List, Any

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
    self._event_handler = event_handler
    self._initial_values = kwargs.get('initial_values')
    self._command_mapping = {}
    self._actions = []


    # If alias given but no ID look at config files for ID.
    if not ff_id and alias:
      if aliases.get_device_id(alias):
        ff_id = aliases.get_device_id(alias)

    elif ff_id and not alias:
      if aliases.get_alias(ff_id):
        alias = aliases.get_alias(ff_id)

    # If no ff_id ID given -> generate random ID.
    if not ff_id:
      ff_id = str(uuid.uuid4())

    self._id = ff_id
    self._alias = alias if alias else ff_id
    aliases.set_alias(self._id, self._alias)

    self._triggers = Triggers(firefly, ff_id)

    triggers = kwargs.get('triggers')
    if triggers:
      self.import_triggers(triggers)

    conditions = kwargs.get('conditions')
    if conditions:
      self._conditions = Conditions(**conditions)
    else:
      self._conditions = None

    actions = kwargs.get('actions')
    if actions:
      for action in actions:
        self._actions.append(Action(**action))


  def request(self, request: Request) -> Any:
    """Function to request data from the ff_id.

    The returned data can be in any format. Common formats should be:
      str, int, dict

    Args:
      request (Request): Request object

    Returns:
      Requested Data

    """
    logging.debug('%s: Got Request %s' % (self.id, request))
    if request.request == API_INFO_REQUEST:
      return self.get_api_info()
    return None


  def get_api_info(self) -> dict:
    """
    Function to get view for API.

    Returns (dict): JSON for API view.

    """
    return_data = {}
    return_data.update(self.export(api_view=True))
    return return_data

  def import_triggers(self, triggers):
    logging.info('Importing triggers into %s - %s' % (self.id, triggers))
    self.triggers.import_triggers(triggers)

  def export_triggers(self):
    logging.info('Exporting triggers into %s' % self.id)
    return self.triggers.export()

  def add_trigger(self, trigger, **kwargs):
    self.triggers.add_trigger(trigger)

  def remove_trigger(self, trigger, **kwargs):
    self.triggers.remove_trigger(trigger)

  def add_action(self, action):
    if type(action) is dict:
      action = Action(**action)
    if action not in self.actions:
      self.actions.append(action)


  def event(self, event, **kwargs):
    logging.info('[AUTOMATION] %s - Receiving event: %s' % (self.id, event))
    valid = True
    if self.conditions:
      valid &= self.conditions.check_conditions(self._firefly)
    valid &= self.triggers.check_triggers(event)
    if valid:
      return self.get_event_handler(event, **kwargs)

  def export(self, **kwargs):
    export_data = {
      'type': self.type,
      'package': self._package,
      'ff_id': self.id,
      'actions': self.actions_export,
      'conditions': self.conditions_export,
      'triggers': self.triggers.export(),
      'initial_values': 'TODO INITIAL VALUES',
      'alias': self._alias
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
  def actions(self) -> List[Action]:
    return self._actions

  @property
  def actions_export(self):
    exported_actions = []
    for act in self._actions:
      print(act)
      print(type(act))
      exported_actions.append(act.export())
    return exported_actions

  @property
  def conditions_export(self):
    if self.conditions is None:
      return {}
    return self.conditions.export()

  @property
  def triggers(self):
    return self._triggers

  @property
  def id(self):
    return self._id

  @property
  def conditions(self) -> Conditions:
    return self._conditions

  @property
  def get_event_handler(self):
    return self._event_handler

  @property
  def alias(self):
    return self._alias

  @property
  def type(self):
    return TYPE_AUTOMATION