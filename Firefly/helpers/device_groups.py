from Firefly import logging
from Firefly.util import get_kwargs_value
from typing import Dict

GROUP = 'group'
ROOM = 'room'
ZONE = 'zone'

class DeviceGroups(object):
  def __init__(self, firefly):
    self.firefly = firefly

    self._groups = Groups(self)
    self._rooms = Rooms(self)
    self._zones = Zones(self)

  @property
  def groups(self):
    return self._groups

  @property
  def rooms(self):
    return self._rooms

  @property
  def zones(self):
    return self._zones








class Groups(object):
  def __init__(self, device_groups):
    logging.info('Initialized Groups')
    self._groups: Dict[str,Group] = {}

  def add_group(self, id=None, alias=None, **kwargs):
    if id in self._groups.keys():
      return False
    new_group = Group(id, alias, **kwargs)
    self._groups[new_group.ff_id] = new_group
    return new_group.ff_id

  def add_device(self, group_id, ff_id):
    if group_id not in self._groups:
      return False
    return self._groups[group_id].add_device(ff_id)


class Rooms(object):
  def __init__(self, device_groups):
    logging.info('Initialized Rooms')
    self._rooms: Dict[str,Room] = {}

  def add_room(self, id:str='', alias:str='', **kwargs):
    """
    Add a new room in the rooms object.
    Args:
      id (str): ID of new room (optional)
      alias (str): Alias of new room (optional)
      **kwargs ():

    Returns (str): ff_id of new room

    """
    if id in self._rooms.keys():
      return False
    new_room = Room(id, alias, **kwargs)
    self._rooms[new_room.ff_id] = new_room
    return new_room.ff_id

  def add_device(self, room_id:str, ff_id:str):
    """
    Add a device to a room. A device can only belong to one room.
    Args:
      room_id (str): The ID of the room adding the device to.
      ff_id (str): The ff_id of the device you are adding to the room.

    Return (bool): The device was successfully added to the room.

    """
    if ff_id in self.all_devices:
      logging.error('Error adding devices to room. Device is already in a room.')
      return False
    if room_id not in self.rooms.keys():
      logging.error('Error adding devices to room. Room ID not found')
      return False
    self.rooms[room_id].add_device(ff_id)
    return True

  def get_devices(self, room_id:str):
    """
    Get devices in a room
    Args:
      room_id (str): The room id of the room to get devices of.

    Returns (list): The list of ff_ids of the devices in the room.

    """
    if room_id not in self.rooms.keys():
      logging.error('Error adding devices to room. Room ID not found')
      return []
    return self.rooms[room_id].devices

  @property
  def all_devices(self):
    """
    Get all device ids in all rooms.

    Returns (list): a list of all the ff_ids of devices in all rooms.

    """
    devices = []
    for r_id, room in self.rooms.items():
      devices.append(room.devices)
    devices = list(set(devices))
    return devices

  @property
  def rooms(self):
    return self._rooms


class Zones(object):
  def __init__(self, device_groups):
    logging.info('Initialized Zones')
    self._zones = {}

  def add_zone(self, id=None, alias=None, **kwargs):
    if id in self._zones.keys():
      return False
    new_zone = Zone(id, alias, **kwargs)
    self._zones[new_zone.ff_id] = new_zone
    return new_zone.ff_id






class DeviceGroup(object):
  def __init__(self, id, alias, **kwargs):
    self._id = id
    self._alias = alias
    self._group_type = get_kwargs_value(kwargs, 'group_type', GROUP)
    self._devices = []


  def add_device(self, ff_id):
    if ff_id not in self.devices:
      self._devices.append(ff_id)

  @property
  def devices(self):
    return self._devices

  @property
  def ff_id(self):
    return self._id

  @property
  def type(self):
    return self._group_type

class Group(DeviceGroup):
  def __init__(self, id, alias, **kwargs):
    super().__init__(id, alias, **kwargs)
    if 'group_type' not in kwargs.keys():
      kwargs['group_type'] = GROUP
    super().__init__(id, alias, **kwargs)

class Room(DeviceGroup):
  def __init__(self, id, alias, **kwargs):
    super().__init__(id, alias, **kwargs)
    if 'group_type' not in kwargs.keys():
      kwargs['group_type'] = ROOM
    super().__init__(id, alias, **kwargs)


class Zone(DeviceGroup):
  def __init__(self, id, alias, **kwargs):
    super().__init__(id, alias, **kwargs)
    if 'group_type' not in kwargs.keys():
      kwargs['group_type'] = ZONE
    super().__init__(id, alias, **kwargs)



