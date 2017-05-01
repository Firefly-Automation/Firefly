import uuid
from typing import Any, Callable

from Firefly import aliases, logging
from Firefly.const import API_INFO_REQUEST, EVENT_TYPE_BROADCAST, TYPE_DEVICE
from Firefly.helpers.events import Command, Event, Request
import asyncio

class Device(object):
  def __init__(self, firefly, package, title, author, commands, requests, device_type, **kwargs):
    device_id = kwargs.get('ff_id')
    alias = kwargs.get('alias')

    self._firefly = firefly
    self._title = title
    self._author = author
    self._package = package
    # TODO: Change commands and requests to set
    self._commands = list(set(commands))
    self._requests = list(set(requests))
    self._device_type = device_type
    self._export_ui = True
    self._initial_values = kwargs.get('initial_values')
    self._command_mapping = {}
    self._request_mapping = {}
    self._metadata = {
      'title':   self._title,
      'author':  self._author,
      'package': self._package,
      'actions': {}
    }
    self._last_command_source = 'none'
    self._last_update_time = self.firefly.location.now

    # If alias given but no ID look at config files for ID.
    if not device_id and alias:
      if aliases.get_device_id(alias):
        device_id = aliases.get_device_id(alias)
        if device_id in self.firefly.components:
          device_id = None

    elif device_id and not alias:
      if aliases.get_alias(device_id):
        alias = aliases.get_alias(device_id)

    # If no ff_id ID given -> generate random ID.
    if not device_id:
      device_id = str(uuid.uuid4())

    self._id = device_id
    self._alias = alias if alias else device_id
    self._alias = aliases.set_alias(self._id, self._alias)

    self._habridge_export = kwargs.get('habridge_export', True)
    self._habridge_alias = kwargs.get('habridge_alias', self._alias)
    self._homekit_export = kwargs.get('homekit_export', True)
    self._homekit_alias = kwargs.get('homekit_alias', self._alias)
    self._homekit_types = {}
    self._room = kwargs.get('room', '')
    self._tags = kwargs.get('tags', [])

  def __str__(self):
    return '< FIREFLY DEVICE - ID: %s | PACKAGE: %s >' % (self.id, self._package)

  def export(self, current_values: bool = True, api_view: bool = False) -> dict:
    """
    Export ff_id config with options current values to a dictionary.

    Args:
      current_values (bool): Include current values as new initial values.

    Returns:
      (dict): A dict of the ff_id config.
    """
    export_data = {
      'package':         self._package,
      'ff_id':           self.id,
      'alias':           self._alias,
      'type':            self.type,
      'homekit_export':  self._homekit_export,
      'homekit_alias':   self._homekit_alias,
      'homekit_types':   self._homekit_types,
      'habridge_export': self._habridge_export,
      'habridge_alias':  self._habridge_alias,
      'export_ui':       self._export_ui,
      'tags': self._tags,
      'room': self._room
    }

    if current_values:
      current_vals = {}
      for item in self._initial_values.keys():
        current_vals[item] = self.__getattribute__(item)

      export_data['initial_values'] = current_vals

    return export_data

  def add_command(self, command: str, function: Callable) -> None:
    """
    Adds a command to the list of supported ff_id commands.

    Args:
      command (str): The string of the command
      function (Callable): The function to be executed.
    """
    self._command_mapping[command] = function

  def add_request(self, request: str, function: Callable) -> None:
    """
    Adds a request to the list of supported ff_id requests.

    Args:
      request (str): The string of the request
      function (Callable): The function to be executed.
    """
    self._request_mapping[request] = function

  def add_action(self, action, action_meta):
    self._metadata['actions'][action] = action_meta

  def add_homekit_export(self, homekit_type, action):
    self._homekit_types[homekit_type] = action

  def command(self, command: Command) -> bool:
    """
    Function that is called to send a command to a ff_id.
    Args:
      command (Command): The command to be sent in a Command object

    Returns:
      (bool): Command successful.
    """
    state_before = self.get_all_request_values()
    logging.debug('%s: Got Command: %s' % (self.id, command.command))
    if command.command in self.command_map.keys():
      self._last_command_source = command.source
      self._last_update_time = self.firefly.location.now
      try:
        self.command_map[command.command](**command.args)
      except:
        return False
      state_after = self.get_all_request_values()
      self.broadcast_changes(state_before, state_after)
      return True
    return False

  def broadcast_changes(self, before: dict, after: dict) -> None:
    """Find changes from before and after states and broadcast the changes.

    Args:
      before (dict): before state.
      after (dict): after state.

    Returns:

    """
    if before == after:
      logging.debug('No change detected. %s' % self)
      return
    logging.debug('Change detected. %s' % self)
    changed = {}
    for item, val in after.items():
      if after.get(item) != before.get(item):
        changed[item] = after.get(item)
    logging.debug("Items changed: %s %s" % (str(changed), self))
    broadcast = Event(self.id, EVENT_TYPE_BROADCAST, event_action=changed)
    logging.info(broadcast)
    self._firefly.send_event(broadcast)
    return

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
    if request.request in self.request_map.keys():
      return self.request_map[request.request](**request.args)
    return None

  def event(self, event: Event) -> None:
    logging.error(code='FF.DEV.EVE.001')  # devices currently dont support events

  def get_api_info(self) -> dict:
    """
    Function to get view for API.

    Returns (dict): JSON for API view.

    """
    return_data = {}
    return_data.update(self.export(api_view=True))
    return_data['commands'] = self._commands
    return_data['requests'] = self._requests
    return_data['device_type'] = self._device_type
    return_data['metadata'] = self._metadata
    return_data['current_values'] = return_data['initial_values']
    return_data['last_update_time'] = str(self._last_update_time)
    return_data['last_command_source'] = self._last_command_source
    return_data.pop('initial_values')
    return_data['request_values'] = {}
    for r in self._requests:
      return_data['request_values'][r] = self.request_map[r]()
    return return_data

  def get_all_request_values(self) -> dict:
    """Function to get all requestable values.

    Returns (dict): All requests and values.

    """
    request_values = {}
    for r in self._requests:
      request_values[r] = self.request_map[r]()
    return request_values

  def member_set(self, key: str, val: Any) -> None:
    """Function for setting member values when you want it to be broadcasted.

    This is mainly used for time delay functions and it similar to the builtin __setattr__.

    Args:
      key (string): Value to be changed.
      val (Any): New value.

    Returns:

    """
    logging.info("Setting %s to %s" % (key, val))
    state_before = self.get_all_request_values()
    self.__setattr__(key, val)
    state_after = self.get_all_request_values()
    self.broadcast_changes(state_before, state_after)

  # TODO: Add runInX functions to devices. These functions have to be similar to member_set and should be able to replace it.

  @property
  def id(self):
    return self._id

  @property
  def firefly(self):
    return self._firefly

  @property
  def command_map(self):
    return self._command_mapping

  @property
  def request_map(self):
    return self._request_mapping

  @property
  def tags(self):
    return self._tags

  @property
  def room(self):
    return self._room

  @property
  def type(self):
    return TYPE_DEVICE