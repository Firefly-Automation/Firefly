import json
from typing import Callable
from uuid import uuid4

from Firefly import aliases, logging
from Firefly.const import ACTION_OFF, ACTION_ON, CONTACT, CONTACT_CLOSED, CONTACT_OPEN, EVENT_TYPE_BROADCAST, GROUPS_CONFIG_FILE, LEVEL, MOTION, MOTION_ACTIVE, MOTION_INACTIVE, STATE, SWITCH
from Firefly.helpers.events import Command, Event, Request
from Firefly.helpers.metadata import action_on_off_switch, action_motion, action_contact

'''
devices[ff_id] = {tags: [tags], values: {prop: value}}
'''

TAG_MAP = {
  'switch':   [SWITCH, STATE],
  'light':    [SWITCH, STATE, LEVEL],
  'dimmer':   [SWITCH, STATE, LEVEL],
  'outlet':   [SWITCH, STATE],
  'fan':      [SWITCH, STATE, LEVEL],

  # Contact sensors
  'contact':  [CONTACT, 'alarm'],
  'window':   [CONTACT, 'alarm'],
  'door':     [CONTACT, 'alarm'],

  # Motion
  'motion':   [MOTION, 'alarm'],

  # Security
  'security': [MOTION, CONTACT, STATE]

  # TODO: Items below
  # lux
  # battery
  # security - Contact/Motion sensors can also be tagged security

}


# TODO: New sample groups config
# TODO: add groups export to shutdown
# TODO: After adding flag to refresh metadata for firebase, refresh when capabilities change.


def import_groups(firefly, config_file=GROUPS_CONFIG_FILE):
  """Simple function to import groups into firefly from config file

  Args:
    firefly: firefly object
    config_file: groups config file (defaalt in config folder)
  """
  with open(config_file) as gc:
    groups_config = json.loads(gc.read())
    for ff_id, group in groups_config.items():
      new_group = Group(firefly, ff_id=ff_id, **group)
      firefly.components[ff_id] = new_group


def export_groups(firefly, config_file=GROUPS_CONFIG_FILE):
  """Simple function to export groups.

  Args:
    firefly: firefly object
    config_file: path to config file (default to config folder)
  """
  export_data = {}
  for ff_id, component in firefly.components.items():
    if component.type != 'GROUP':
      continue
    export_data[ff_id] = component.export()

  with open(config_file, 'w') as f:
    json.dump(export_data)


def make_group(firefly, alias):
  """ Function to make group.

  Returns:
    group_id: ff_id of new group
  """
  new_group = Group(firefly, alias)
  firefly.components[new_group.id] = new_group
  return new_group.id


class Group(object):
  def __init__(self, firefly, alias, **kwargs):
    self.firefly = firefly

    self.device_list = kwargs.get('devices', [])
    self.devices = {}
    self.requests = []
    self.command_mapping = {}
    self.request_mapping = {}
    self.metadata = {
      'actions': {}
    }

    self.add_request(SWITCH, self.get_switch_switch)
    self.add_action(SWITCH, action_on_off_switch(False, 'Switches'))

    self.add_request('light', self.get_light_switch)
    self.add_action('light', action_on_off_switch(False, 'Lights', request='light'))

    self.add_request('dimmer', self.get_dimmer)


    # TODO: the requests below and lux, water sensor, presence.
    # TODO: current state of these requests need to be uploaded to GroupStatus
    # TODO: Documentation on groups

    self.add_request('contact', self.get_contact_contact)
    self.add_action('contact', action_contact(False, 'Contact Sensors'))

    self.add_request('door', self.get_door_contact)
    self.add_action('door', action_contact(False, 'Door Sensors', request='door'))

    self.add_request('window', self.get_window_contact)
    self.add_action('window', action_contact(False, 'Window Sensors', request='window'))

    self.add_request('motion', self.get_motion_motion)
    self.add_action('motion', action_motion(False))

    self.add_request('security', self.get_security)

    # self.add_request('alarm', self.get_alarm)

    # Warnings (low battery etc)
    # self.add_request('warnings', self.get_warnings)


    if kwargs.get('ff_id') is not None:
      self.ff_id = kwargs['ff_id']
    else:
      logging.debug('[GROUP] Setting new FFID')
      ff_id = aliases.get_device_id(alias)
      if ff_id:
        self.ff_id = ff_id
      else:
        self.ff_id = str(uuid4())

    self.alias = aliases.set_alias(self.ff_id, alias)

    for d in self.device_list:
      self.add_device(d)

  # Functions to get switch states
  def get_switch(self, tag, **kwargs):
    '''Get switch states for lights'''
    switch_state = False
    devices = self.get_devices_by_tags([tag])
    for device in devices:
      switch_state |= self.devices[device]['state'].get(SWITCH) == ACTION_ON
    return ACTION_ON if switch_state else ACTION_OFF

  def get_switch_switch(self, **kwargs):
    '''Get switch states for lights'''
    return self.get_switch('switch')

  def get_light_switch(self, **kwargs):
    '''Get switch states for lights'''
    return self.get_switch('light')

  # Functions for contact sensors
  def get_contact(self, tag, **kwargs):
    contact_state = True
    devices = self.get_devices_by_tags([tag])
    for device in devices:
      if 'contact' not in self.devices[device]['tags'] and 'window' not in self.devices[device]['tags'] and 'door' not in self.devices[device]['tags']:
        continue
      contact_state &= self.devices[device]['state'].get(CONTACT) == CONTACT_CLOSED
    return CONTACT_CLOSED if contact_state else CONTACT_OPEN

  def get_window_contact(self, **kwargs):
    return self.get_contact('window')

  def get_door_contact(self, **kwargs):
    return self.get_contact('door')

  def get_contact_contact(self, **kwargs):
    return self.get_contact(CONTACT)

  # Function to get motion
  def get_motion(self, tag, **kwargs):
    motion_state = False
    devices = self.get_devices_by_tags([tag])
    for device in devices:
      if MOTION not in self.devices[device]['tags']:
        continue
      motion_state |= self.devices[device]['state'].get(MOTION) == MOTION_ACTIVE
    return MOTION_ACTIVE if motion_state else MOTION_INACTIVE

  def get_motion_motion(self, **kwargs):
    return self.get_motion(MOTION)

  # Security functions
  def get_security(self, **kwargs):
    secured = True
    secured &= self.get_motion('security') == MOTION_INACTIVE
    secured &= self.get_contact('security') == CONTACT_CLOSED
    return secured

  # Functions for dimmers
  def get_dimmer(self, **kwargs):
    '''Get avg light level for all lights'''
    light_level = 0
    devices = self.get_devices_by_tags(['dimmer'])
    if len(devices) == 0:
      return 0
    for device in devices:
      light_level += self.devices[device]['state'].get('level')
    return light_level / len(devices)

  def export(self, **kwargs):
    export_data = {
      'ff_id':   self.id,
      'alias':   self.alias,
      'devices': list(self.devices.keys())
    }
    return export_data

  def get_metadata(self, **kwargs):
    metadata = {
      'ff_id':   self.id,
      'alias':   self.alias,
      'devices': self.devices,
      'tags': self.get_all_tags(),
      'metadata': self.metadata
    }
    return metadata

  def add_device(self, ff_id):
    if ff_id not in self.firefly.components:
      logging.error('[GROUP] ff_id: %s not found in components' % ff_id)
      return
    # try:
    tags = self.firefly.components[ff_id].tags
    logging.message(str(tags))
    self.devices[ff_id] = {
      'tags':  tags,
      'state': {}
    }
    self.get_device_values(ff_id)
    self.firefly.subscriptions.add_subscriber(self.id, ff_id)
    # except Exception as e:
    #  logging.error('[GROUP] tags function not found for ff_id: %s - %s' % (ff_id, str(e)))

  def get_device_values(self, ff_id, **kwargs):
    tags = self.devices[ff_id]['tags']
    requests = set()
    for tag in tags:
      requests.update(TAG_MAP[tag])
    requests = list(requests)
    for r in requests:
      request = Request(ff_id, self.id, r)
      value = self.firefly.components[ff_id].request(request)
      if value:
        self.devices[ff_id]['state'][r] = value

  def command(self, command: Command) -> bool:
    """
    Function that is called to send a command to a ff_id.
    Args:
      command (Command): The command to be sent in a Command object

    Returns:
      (bool): Command successful.
    """
    logging.debug('%s: Got Command: %s' % (self.id, command.command))
    # if command.command in self.command_map.keys():
    # self._last_command_source = command.source
    # self._last_update_time = self.firefly.location.now
    # TODO Clean up whats not used here
    self.execute_command(command)
    return True

  def execute_command(self, command: Command, **kwargs):
    tags = command.args.get('tags', 'all')

    if tags == 'all':
      devices = self.get_device_list()
    else:
      devices = self.get_devices_by_tags(tags)

    for device in devices:
      c = Command(device, command.source, command.command, **command.args)
      self.firefly.send_command(c)

  def get_devices_by_tags(self, tags, **kwargs):
    devices = set()
    for tag in tags:
      for ff_id, device in self.devices.items():
        if tag in device['tags']:
          devices.add(ff_id)
    return list(devices)


  def get_all_tags(self, **kwargs):
    tags = set()
    for ff_id, device in self.devices.items():
      tags.update(device['tags'])
    return list(tags)

  def get_device_list(self, **kwargs):
    return list(self.devices.keys())

  def event(self, event: Event) -> None:
    logging.info('[GROUP] received event %s' % event)
    state_before = self.get_all_request_values()

    self.devices[event.source]['state'].update(event.event_action)

    state_after = self.get_all_request_values()
    self.broadcast_changes(state_before, state_after)

  def get_all_request_values(self) -> dict:
    """Function to get all requestable values.

    Returns (dict): All requests and values.

    """
    request_values = {}
    for r in self.requests:
      request_values[r] = self.request_map[r]()
    return request_values

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
    self.firefly.send_event(broadcast)
    return

  def add_command(self, command: str, function: Callable) -> None:
    """
    Adds a command to the list of supported ff_id commands.

    Args:
      command (str): The string of the command
      function (Callable): The function to be executed.
    """
    self.command_mapping[command] = function

  def add_request(self, request: str, function: Callable) -> None:
    """
    Adds a request to the list of supported ff_id requests.

    Args:
      request (str): The string of the request
      function (Callable): The function to be executed.
    """
    self.requests.append(request)
    self.request_mapping[request] = function

  def add_action(self, action, action_meta):
    self.metadata['actions'][action] = action_meta
    if action_meta.get('primary') is True:
      self.metadata['primary'] = action

  @property
  def id(self):
    return self.ff_id

  @property
  def type(self):
    return 'GROUP'

  @property
  def command_map(self):
    return self.command_mapping

  @property
  def request_map(self):
    return self.request_mapping
