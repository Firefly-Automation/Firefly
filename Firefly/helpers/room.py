import uuid
from time import sleep
from typing import Any, Callable

from Firefly import aliases, logging, scheduler
from Firefly.const import (API_INFO_REQUEST, CONTACT, CONTACT_CLOSED, CONTACT_OPEN, EVENT_ACTION_ANY,
                           EVENT_TYPE_BROADCAST, LEVEL, LUX, MOTION, MOTION_ACTIVE, MOTION_INACTIVE, SWITCH, SWITCH_OFF,
                           SWITCH_ON, TYPE_DEVICE)
from Firefly.helpers.events import Command, Event, Request

# TODO: These should be moved into the const file
# Tag Lookups are used to know what properties to look for
TAG_LOOKUPS = {
  # SWITCH_OPEN SWITCH_CLOSED
  'switch':  SWITCH,
  'light':   SWITCH,
  'dimmer':  SWITCH,
  'outlet':  SWITCH,
  'fan':     SWITCH,

  # CONTACT_OPEN, CONTACT_CLOSED
  'window':  CONTACT,
  'door':    CONTACT,
  'contact': CONTACT,

  # MOTION_ACTIVE, MOTION_INACTIVE
  'motion':  MOTION,

  # Take avg of all lux sensors
  'lux':     LUX,
  'water':   'water'
}

TAG_PROPS = {
  SWITCH:  {
    True:  SWITCH_ON,
    False: SWITCH_OFF
  },
  CONTACT: {
    True:  CONTACT_OPEN,
    False: CONTACT_CLOSED
  },
  MOTION:  {
    True:  MOTION_ACTIVE,
    False: MOTION_INACTIVE
  }
}

REQUESTS = [SWITCH, LEVEL, CONTACT, MOTION, 'outlet']


class Rooms(object):
  def __init__(self, firefly, **kwargs):
    self.firefly = firefly
    self._rooms = {}

  def build_rooms(self):
    for c in self.firefly.components.values():
      print(c)

      if c.type != TYPE_DEVICE:
        continue
      if c.room is None:
        continue
      if c.room not in self._rooms.keys() and c.room != '':
        self._rooms[c.room] = Room(self.firefly, c.room)
      print(c.room)
      if c.room != '':
        self._rooms[c.room].add_device(c.id, c.tags)

    for _, r in self._rooms.items():
      self.firefly.components[r.id] = r

  @property
  def type(self):
    return 'ROOM'


"""Please note that rooms are based off of devices, any major changes to devices should be copied here"""


class Room(object):
  def __init__(self, firefly, alias, **kwargs):
    self._alias = alias
    self._devices = kwargs.get('devices', {})
    self._tags = set()
    self.firefly = firefly
    self._requests = []
    self._command_mapping = {}
    self._request_mapping = {}
    self._last_command_source = 'none'
    self._last_update_time = self.firefly.location.now

    device_id = kwargs.get('ff_id')

    if not device_id:
      if aliases.get_device_id(alias):
        device_id = aliases.get_device_id(alias)

    if not device_id:
      device_id = str(uuid.uuid4())

    self._id = device_id
    self._alias = aliases.set_alias(self._id, self._alias)

    for d in self._devices:
      self.firefly.subscriptions.add_subscriber(self.id, d)

    self._switch = SWITCH_OFF
    self.add_request(SWITCH, self.switch_state)

    self._light = SWITCH_OFF
    self.add_request('light', self.light_state)

    self._motion = MOTION_INACTIVE
    self.add_request('motion', self.motion_state)

    self._contact = CONTACT_CLOSED
    self.add_request(CONTACT, self.contact_state)

    self._outlet = SWITCH_OFF
    self.add_request('outlet', self.outlet_state)

    scheduler.runEveryM(5, self.force_check_status, job_id='%s-force_check' % self.id)

  def add_device(self, ff_id, tags):
    self._devices[ff_id] = {
      'tags':  tags,
      'state': {}
    }
    requests = set(TAG_LOOKUPS[t] for t in tags)
    for r in requests:
      try:
        request = Request(ff_id, self.id, r)
        self._devices[ff_id]['state'][r] = self.firefly.components[ff_id].request(request)
        self.firefly.subscriptions.add_subscriber(self.id, ff_id, {
          r: EVENT_ACTION_ANY
        })
        self._tags.update(tags)
      except:
        logging.error(code='FF.ROO.ADD.001', args=(ff_id, r))  # device %s does not have request %s

  def event(self, event: Event) -> None:
    logging.info('[ROOM] received event %s' % event)
    state_before = self.get_all_request_values()

    # TODO check if list of device > 0 before setting to true
    if SWITCH in event.event_action.keys() and event.source in self._devices:
      self._devices[event.source]['state'][SWITCH] = event.event_action[SWITCH]

    if MOTION in event.event_action.keys() and event.source in self._devices:
      self._devices[event.source]['state'][MOTION] = event.event_action[MOTION]
    self.check_states()

    if CONTACT in event.event_action.keys() and event.source in self._devices:
      self._devices[event.source]['state'][CONTACT] = event.event_action[CONTACT]

    self.check_states()

    state_after = self.get_all_request_values()
    self.broadcast_changes(state_before, state_after)

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

  def get_all_request_values(self, min_data=False, **kwargs) -> dict:
    """Function to get all requestable values.

    Returns (dict): All requests and values.

    Args:
      min_data (bool): only get requests that are lowercase. This is used for firebase and filtering out unneeded data.

    """
    request_values = {}
    for r in self._requests:
      if not min_data or r.islower():
        request_values[r] = self.request_map[r]()
    return request_values

  def check_states(self):
    for tag, prop in TAG_LOOKUPS.items():
      if prop not in TAG_PROPS.keys():
        # TODO Fix This
        logging.warn('PROP NOT SUPPORTED YET: %s' % prop)
        continue
      self.check_tag_status(tag, '_%s' % tag, TAG_PROPS[prop][True], TAG_PROPS[prop][False])

  def check_tag_status(self, tag, attr, true_state, false_state):
    value = False
    for d in set([d for d, t in self._devices.items() if tag in t['tags']]):
      value |= self._devices[d]['state'][TAG_LOOKUPS[tag]] == true_state
    self.__setattr__(attr, true_state if value else false_state)

  def force_check_status(self):
    for dev, vals in self._devices.items():
      tags = vals.get('tags', [])
      requests = set(TAG_LOOKUPS[t] for t in tags)
      for r in requests:
        try:
          request = Request(dev, self.id, r)
          self._devices[dev]['state'][r] = self.firefly.components[dev].request(request)
        except:
          logging.error(code='FF.ROO.FOR.001', args=(dev, r))  # device %s does not have request %s

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

  def get_api_info(self) -> dict:
    """
    Function to get view for API.

    Returns (dict): JSON for API view.

    """
    self.check_states()
    return_data = {
      'type':           self.type,
      'alias':          self.alias,
      'ff_id':          self.id,
      'devices':        self._devices,
      'request_values': {}
    }
    for r in self._requests:
      return_data['request_values'][r] = self.request_map[r]()
    return return_data

  def command(self, command: Command) -> bool:
    """
    Function that is called to send a command to a ff_id.
    Args:
      command (Command): The command to be sent in a Command object

    Returns:
      (bool): Command successful.
    """
    # state_before = self.get_all_request_values()
    logging.debug('%s: Got Command: %s' % (self.id, command.command))
    # if command.command in self.command_map.keys():
    self._last_command_source = command.source
    self._last_update_time = self.firefly.location.now
    # TODO Clean up whats not used here
    self.execute_command(command)
    # self.command_map[command.command](**command.args)
    # state_after = self.get_all_request_values()
    # self.broadcast_changes(state_before, state_after)
    return True
    # return False

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
    self._requests.append(request)
    self._request_mapping[request] = function

  def execute_command(self, command: Command):
    print(command.args)
    tags = command.args.get('tags', [])
    if type(tags) is str and tags != 'all':
      tags = [tags]

    if tags == []:
      tags = 'all'

    if tags == 'all':
      devices = set(self._devices)
    else:
      devices = set([d for d, t in self._devices.items() if bool(set(t['tags']) & set(tags))])
    for d in devices:
      c = Command(d, command.source, command.command, **command.args)
      self.firefly.send_command(c)
      sleep(0.01)

  def switch_state(self):
    return self._switch

  def light_state(self):
    return self._light

  def motion_state(self):
    return self._motion

  def contact_state(self):
    return self._contact

  def outlet_state(self):
    return self._outlet

  @property
  def id(self):
    return self._id

  @property
  def alias(self):
    return self._alias

  @property
  def type(self):
    return 'ROOM'

  @property
  def command_map(self):
    return self._command_mapping

  @property
  def request_map(self):
    return self._request_mapping
