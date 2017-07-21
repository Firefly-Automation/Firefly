from Firefly import logging, scheduler
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import (ACTION_ENABLE_BEACON, ACTION_NOT_PRESENT, ACTION_NOT_PRESENT_BEACON, ACTION_PRESENT,
                           ACTION_PRESENT_BEACON, ACTION_SET_DELAY, BEACON_ENABLED, DEVICE_TYPE_PRESENCE, ENABLED,
                           NOT_ENABLED, NOT_PRESENT, PRESENCE, PRESENT)
from Firefly.helpers.device import Device
from Firefly.helpers.metadata import metaPresence
from Firefly.helpers.action import Command

TITLE = 'Firefly Virtual Presence Device'
DEVICE_TYPE = DEVICE_TYPE_PRESENCE
AUTHOR = AUTHOR
COMMANDS = [ACTION_PRESENT, ACTION_NOT_PRESENT, ACTION_PRESENT_BEACON, ACTION_NOT_PRESENT_BEACON, ACTION_ENABLE_BEACON,
  PRESENCE, ACTION_SET_DELAY]
REQUESTS = [PRESENCE, BEACON_ENABLED, 'beacon_presence', 'raw_presence', 'firebase_api_key']
INITIAL_VALUES = {
  '_delay':           300,
  '_presence':        NOT_PRESENT,
  '_beacon_enabled':  NOT_ENABLED,
  '_beacon_presence': NOT_PRESENT,
  '_raw_presence':    NOT_PRESENT,
}


def Setup(firefly, package, **kwargs):
  """

  Args:
      firefly:
      package:
      kwargs:
  """
  logging.message('Entering %s setup' % TITLE)
  new_presence = VirtualPresence(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_presence.id] = new_presence


class VirtualPresence(Device):
  """
  """

  def __init__(self, firefly, package, **kwargs):
    """

    Args:
        firefly:
        package:
        kwargs:
    """
    if kwargs.get('initial_values'):
      INITIAL_VALUES.update(kwargs.get('initial_values'))
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self.add_command(PRESENCE, self.set_presence)
    self.add_command(ACTION_PRESENT, self.set_present)
    self.add_command(ACTION_NOT_PRESENT, self.set_not_present)
    self.add_command(ACTION_PRESENT_BEACON, self.set_beacon_present)
    self.add_command(ACTION_NOT_PRESENT_BEACON, self.set_beacon_not_present)
    self.add_command(ACTION_ENABLE_BEACON, self.set_beacon_enabled)
    self.add_command(ACTION_SET_DELAY, self.set_delay)

    self.add_request(PRESENCE, self.get_presence)
    self.add_request(BEACON_ENABLED, self.get_beacon_enabled)
    self.add_request('beacon_presence', self.get_beacon_presence)
    self.add_request('raw_presence', self.get_raw_presence)
    self.add_request('firebase_api_key', self.get_firebase_api_key)

    self.add_action(PRESENCE, metaPresence(primary=True))

    # TODO: Make HOMEKIT CONST
    self.add_homekit_export('HOMEKIT_PRESENCE', PRESENCE)

    self._alexa_export = False
    self.firebase_api_key = kwargs.get('firebase_api_key', None)
    if self.firebase_api_key is None and self.firefly.firebase_enabled:
      self.register_firebase()

  def export(self, current_values: bool = True, api_view: bool = False):
    export_data = super().export(current_values, api_view)
    export_data['firebase_api_key'] = self.firebase_api_key
    return export_data

  def set_presence(self, **kwargs):
    """

    Args:
        kwargs:
    """
    presence = kwargs.get('presence', False)
    presence = True if presence.lower() == 'true' else False
    presence_string = PRESENT if presence else NOT_PRESENT
    if kwargs.get('type') == 'beacon':
      if presence:
        self._beacon_presence = presence_string
      else:
        scheduler.runInS(self._delay, self._set_beacon_not_present)
    else:
      if presence:
        self._presence = presence_string
        self._raw_presence = presence_string
      else:
        self._raw_presence = NOT_PRESENT
        scheduler.runInS(self._delay, self._set_not_present)

  def set_delay(self, **kwargs):
    """

    Args:
        kwargs:
    """
    delay = int(kwargs.get('delay', 5))
    self._delay = delay

  def set_present(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    self._presence = PRESENT
    self._raw_presence = PRESENT
    return PRESENT

  def set_not_present(self, **kwargs):
    """

    Args:
        kwargs:
    """
    self._raw_presence = NOT_PRESENT
    scheduler.runInS(self._delay, self._set_not_present)

  def set_beacon_present(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    self._beacon_presence = PRESENT
    return PRESENT

  def set_beacon_not_present(self, **kwargs):
    """

    Args:
        kwargs:
    """
    scheduler.runInS(self._delay, self._set_beacon_not_present)

  def _set_beacon_not_present(self, **kwargs):
    """

    Args:
        kwargs:
    """
    self.member_set('_beacon_presence', NOT_PRESENT)

  def _set_not_present(self, **kwargs):
    """

    Args:
        kwargs:
    """
    self.member_set('_presence', NOT_PRESENT)

  def set_beacon_enabled(self, **kwargs):
    """

    Args:
        kwargs:
    """
    enabled = kwargs.get('enabled', False)
    enabled = ENABLED if enabled.lower() == 'true' else NOT_ENABLED
    self._beacon_enabled = enabled

  def get_presence(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    return self.presence

  def get_beacon_enabled(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    return self._beacon_enabled

  @property
  def presence(self):
    """

    Returns:

    """

    presence = True if self._presence == PRESENT else False
    beacon_presence = True if self._beacon_presence == PRESENT else False
    if self._beacon_enabled:
      return PRESENT if presence | beacon_presence else NOT_PRESENT
    return PRESENT if presence else NOT_PRESENT

  def get_beacon_presence(self, **kwargs):
    return self._beacon_presence

  def get_raw_presence(self, **kwargs):
    return self._raw_presence

  def register_firebase(self):
    command = Command('service_firebase', self.id, 'get_api_id', callback=self.set_firebase_api_key, api_ff_id=self.id)
    self.firefly.send_command(command)

  def set_firebase_api_key(self, **kwargs):
    self.firebase_api_key = kwargs.get('firebase_api_key')

  def get_firebase_api_key(self):
    return str(self.firebase_api_key)

