from Firefly import logging
from Firefly.const import (ACTION_PRESENT, ACTION_NOT_PRESENT, PRESENT, NOT_PRESENT, DEVICE_TYPE_PRESENCE,
                           ACTION_PRESENT_BEACON, ACTION_NOT_PRESENT_BEACON, ACTION_ENABLE_BEACON, PRESENCE,
                           BEACON_ENABLED, ENABLED, NOT_ENABLED)
from Firefly.components.virtual_devices import AUTHOR
from Firefly.helpers.device import Device

from Firefly.helpers.metadata import metaPresence

TITLE = 'Firefly Virtual Presence Device'
DEVICE_TYPE = DEVICE_TYPE_PRESENCE
AUTHOR = AUTHOR
COMMANDS = [ACTION_PRESENT, ACTION_NOT_PRESENT, ACTION_PRESENT_BEACON, ACTION_NOT_PRESENT_BEACON, ACTION_ENABLE_BEACON,
            PRESENCE]
REQUESTS = [PRESENCE, BEACON_ENABLED]
INITIAL_VALUES = {
  '_presence':        NOT_PRESENT,
  '_beacon_enabled':  NOT_ENABLED,
  '_beacon_presence': NOT_PRESENT
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_presence = VirtualPresence(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_presence.id] = new_presence


class VirtualPresence(Device):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self.add_command(PRESENCE, self.set_presence)
    self.add_command(ACTION_PRESENT, self.set_present)
    self.add_command(ACTION_NOT_PRESENT, self.set_not_present)
    self.add_command(ACTION_PRESENT_BEACON, self.set_beacon_present)
    self.add_command(ACTION_NOT_PRESENT_BEACON, self.set_beacon_not_present)
    self.add_command(ACTION_ENABLE_BEACON, self.set_beacon_enabled)

    self.add_request(PRESENCE, self.get_presence)
    self.add_request(BEACON_ENABLED, self.get_beacon_enabled)

    self.add_action(PRESENCE, metaPresence(primary=True))

    # TODO: Make HOMEKIT CONST
    self.add_homekit_export('HOMEKIT_PRESENCE', PRESENCE)

  def set_presence(self, **kwargs):
    presence = kwargs.get('PRESENCE', False)
    presence = True if presence.lower() == 'true' else False
    if kwargs.get('TYPE') == 'BEACON':
      self._beacon_presence = presence
    else:
      self._presence = presence

  def set_present(self, **kwargs):
    self._presence = PRESENT

  def set_not_present(self, **kwargs):
    self._presence = NOT_PRESENT

  def set_beacon_present(self, **kwargs):
    self._beacon_presence = PRESENT

  def set_beacon_not_present(self, **kwargs):
    self._beacon_presence = NOT_PRESENT

  def set_beacon_enabled(self, **kwargs):
    enabled = kwargs.get('ENABLED', False)
    enabled = ENABLED if enabled.lower() == 'true' else NOT_ENABLED
    self._beacon_enabled = enabled

  def get_presence(self, **kwargs):
    return self.presence

  def get_beacon_enabled(self, **kwargs):
    return self._beacon_enabled

  @property
  def presence(self):
    if self._beacon_enabled:
      return self._presence & self._beacon_presence
    return self._presence