import uuid
from typing import Any, Callable

from functools import wraps

from Firefly import aliases, logging, scheduler
from Firefly.const import API_ALEXA_VIEW, API_FIREBASE_VIEW, API_INFO_REQUEST, EVENT_TYPE_BROADCAST, TYPE_DEVICE
from Firefly.helpers.events import Command, Event, Request
from Firefly.helpers.metadata import EXPORT_UI, FF_ID, HIDDEN_BY_USER, action_text





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
    self._hidden_by_system = False
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
      if aliases.get_device_id(alias) is not None:
        device_id = aliases.get_device_id(alias)
        if device_id in self.firefly.components:
          device_id = None

    elif device_id and not alias:
      if aliases.get_alias(device_id):
        alias = aliases.get_alias(device_id)

    # If no ff_id ID given -> generate random ID.
    if device_id is None:
      device_id = str(uuid.uuid4())

    self._id = device_id
    self._alias = alias if alias else device_id
    self._alias = aliases.set_alias(self._id, self._alias)

    self._habridge_export = kwargs.get('habridge_export', True)
    self._habridge_alias = kwargs.get('habridge_alias', self._alias)

    self._homekit_export = kwargs.get('homekit_export', True)
    self._homekit_alias = kwargs.get('homekit_alias', self._alias)
    self._homekit_types = {}

    self._alexa_export = kwargs.get('alexa_export', True)
    self._alexa_categories = []
    self._alexa_capabilities = []
    self._alexa_manufacturer_name = kwargs.get('alexa_manufacturer_name', 'Firefly')
    self._alexa_description = kwargs.get('alexa_description', 'Firefly Home Device')

    self._room = kwargs.get('room', '')
    self._tags = kwargs.get('tags', [])

    self.add_command('set_alias', self.set_alias)
    self.add_command('set_room', self.set_room)
    self.add_command('delete', self.delete_device)

    self.add_action('z_last_update', action_text(title='Last Update', request='last_update'))
    self.add_request('last_update', self.last_update)

    # Set initial values
    for prop, val in self._initial_values.items():
      self.__setattr__(prop, val)

    self._before_state = None
    self._after_state = None

  def __str__(self):
    return '< FIREFLY DEVICE - ID: %s | PACKAGE: %s >' % (self.id, self._package)


  def store_before_state(self, **kwargs):
    self._before_state = self.get_all_request_values(True, True)

  def store_after_state(self, **kwargs):
    self._after_state = self.get_all_request_values(True, True)

  def broadcast_change(self, **kwargs):
    if self._before_state is None:
      logging.error('before_sate not recorded')
      return False
    if self._after_state is None:
      self.store_after_state()

    self.broadcast_changes(self._before_state, self._after_state)

    self._before_state = None
    self._after_state = None
    return True

  def set_alias(self, **kwargs):
    new_alias = kwargs.get('alias')
    if new_alias is None:
      return

    self._alias = aliases.set_alias(self._id, new_alias)
    self._habridge_alias = self._alias
    self._homekit_alias = self._alias

    self.firefly.refresh_firebase()

  def set_room(self, **kwargs):
    new_room = kwargs.get('room')
    if new_room is None:
      return

    self._room = new_room
    self.firefly._rooms.build_rooms()

  def delete_device(self):
    self.firefly.delete_device(self.id)
    return

  def last_update(self):
    return '%s (%s)' % (self._last_update_time.strftime("%B %d %Y %I:%M:%S %p"), self._last_command_source)

  def export(self, current_values: bool = True, api_view: bool = False) -> dict:
    """
    Export ff_id config with options current values to a dictionary.

    Args:
      current_values (bool): Include current values as new initial values.

    Returns:
      (dict): A dict of the ff_id config.
    """
    export_data = {
      'package':                 self._package,
      'ff_id':                   self.id,
      'alias':                   self._alias,
      'type':                    self.type,
      'homekit_export':          self._homekit_export,
      'homekit_alias':           self._homekit_alias,
      'homekit_types':           self._homekit_types,
      'habridge_export':         self._habridge_export,
      'habridge_alias':          self._habridge_alias,
      'export_ui':               self._export_ui,
      'tags':                    self._tags,
      'room':                    self._room,
      'alexa_export':            self._alexa_export
    }

    if current_values:
      current_vals = {}
      for item in self._initial_values.keys():
        current_vals[item] = self.__getattribute__(item)

      export_data['initial_values'] = current_vals

    return export_data

  def get_alexa_view(self):
    if self._alexa_export is False:
      return None

    return {
      'endpointId':        self.id,
      'friendlyName':      self.alias,
      'description':       self._alexa_description,
      'manufacturerName':  self._alexa_manufacturer_name,
      'displayCategories': self._alexa_categories,
      'cookie':            {},
      'capabilities':      self._alexa_capabilities
    }

  def add_alexa_capabilities(self, capabilities):
    if type(capabilities) is not list:
      capabilities = [capabilities]
    for capability in capabilities:
      if capability not in self._alexa_capabilities:
        self._alexa_capabilities.append(capability)

  def add_alexa_categories(self, categories):
    if type(categories) is not list:
      categories = [categories]
    for category in categories:
      if category not in self._alexa_categories:
        self._alexa_categories.append(category)

  def set_alexa_categories(self, categories):
    if type(categories) is not list:
      categories = [categories]
    self._alexa_categories = categories

  def add_command(self, command: str, function: Callable) -> None:
    """
    Adds a command to the list of supported ff_id commands.

    Args:
      command (str): The string of the command
      function (Callable): The function to be executed.
    """
    # TODO: Remove this, just use command_map for verification
    if command not in self._commands:
      self._commands.append(command)
    self._command_mapping[command] = function

  def add_request(self, request: str, function: Callable) -> None:
    """
    Adds a request to the list of supported ff_id requests.

    Args:
      request (str): The string of the request
      function (Callable): The function to be executed.
    """
    # TODO: Remove this, just use request_map for verification
    if request not in self._requests:
      self._requests.append(request)
    self._request_mapping[request] = function

  def add_action(self, action, action_meta):
    self._metadata['actions'][action] = action_meta
    if action_meta.get('primary') is True:
      self._metadata['primary'] = action

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
    #state_before = self.get_all_request_values(True, True)
    self.store_before_state()
    logging.debug('%s: Got Command: %s' % (self.id, command.command))
    if command.command in self.command_map.keys():
      self._last_command_source = command.source
      self._last_update_time = self.firefly.location.now
      try:
        self.command_map[command.command](**command.args)
      except:
        return False
      #state_after = self.get_all_request_values(True, True)
      #self.broadcast_changes(state_before, state_after)
      scheduler.runInMCS(5, self.broadcast_change, job_id='%s-b' % self.id, max_instances=1)
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
    changed['last_update'] = self.last_update()
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
    if request.request == API_FIREBASE_VIEW:
      return self.get_firebase_views()
    if request.request == API_ALEXA_VIEW:
      return self.get_alexa_view()
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

  def get_firebase_views(self, **kwargs) -> dict:
    """
    Get the minimum data needed for the web ui for firebase.
    Args:
      **kwargs:

    Returns: (dict) firebase view.

    """
    return_data = {
      FF_ID:          self.id,
      'alias':        self._alias,
      'metadata':     self._metadata,
      'deviceType':   self._device_type,
      'tags':         self._tags,
      'room':         self._room,
      EXPORT_UI:      self._export_ui,
      HIDDEN_BY_USER: self._export_ui
    }
    return return_data

  def get_all_request_values(self, min_data=False, diff_check=False, **kwargs) -> dict:
    """Function to get all requestable values.

    Returns (dict): All requests and values.

    Args:
      min_data (bool): only get requests that are lowercase. This is used for firebase and filtering out unneeded data.

    """
    request_values = {}
    for r in self._requests:
      if diff_check and r == 'last_update':
        continue
      try:
        if not min_data:
          request_values[r] = self.request_map[r]()
          continue
        if min_data and r.islower():
          value = self.request_map[r]()
          if type(value) is float:
            value = round(value, 2)
          request_values[r] = value
      except:
        pass
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
    state_before = self.get_all_request_values(True, True)
    self.__setattr__(key, val)
    state_after = self.get_all_request_values(True, True)
    self.broadcast_changes(state_before, state_after)

  # TODO: Add runInX functions to devices. These functions have to be similar to member_set and should be able to
  # replace it.

  @property
  def id(self):
    return self._id

  @property
  def alias(self):
    return self._alias

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
