from Firefly import logging
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import ACTION_LEVEL, ACTION_OFF, ACTION_ON, ACTION_TOGGLE, DEVICE_TYPE_DIMMER, EVENT_ACTION_LEVEL, EVENT_ACTION_OFF, EVENT_ACTION_ON, LEVEL, STATE
from Firefly.helpers.device import Device
from Firefly.helpers.metadata import metaDimmer, metaSwitch

TITLE = 'Firefly Virtual Dimmer'
DEVICE_TYPE = DEVICE_TYPE_DIMMER
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ACTION_LEVEL]
REQUESTS = [STATE, LEVEL]
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF,
  '_level': 100
}


def Setup(firefly, package, **kwargs):
  """

  Args:
      firefly:
      package:
      kwargs:
  """
  logging.message('Entering %s setup' % TITLE)
  new_switch = VirtualSwitch(firefly, package, **kwargs)
  firefly.install_component(new_switch)
  return new_switch.id


class VirtualSwitch(Device):
  """
  """

  def __init__(self, firefly, package, **kwargs):
    """

    Args:
        firefly:
        package:
        kwargs:
    """
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)
    self.add_command(ACTION_LEVEL, self.set_level)

    self.add_request(STATE, self.get_state)
    self.add_request(LEVEL, self.get_level)

    self.add_action(LEVEL, metaDimmer(primary=True))
    self.add_action(STATE, metaSwitch())

    # TODO: Make HOMEKIT CONST
    self.add_homekit_export('HOMEKIT_DIMMER', LEVEL)

  def off(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    self._state = EVENT_ACTION_OFF
    return EVENT_ACTION_OFF

  def on(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    self._state = EVENT_ACTION_ON
    return EVENT_ACTION_ON

  def toggle(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    if self.state == EVENT_ACTION_ON:
      return self.off()
    return self.on()

  def set_level(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    level = int(kwargs.get('level'))
    event_actions = [EVENT_ACTION_LEVEL]
    if level is None:
      return False
    if level > 100:
      level = 100
    if level == 0 and self.state == EVENT_ACTION_ON:
      self.off()
      event_actions.append(EVENT_ACTION_OFF)
    if level > 0 and self.state == EVENT_ACTION_OFF:
      self.on()
      event_actions.append(EVENT_ACTION_ON)

    self._level = level
    return event_actions

  def get_state(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    return self.state

  def get_level(self, **kwargs):
    """

    Args:
        kwargs:

    Returns:

    """
    return self.level

  @property
  def state(self):
    """

    Returns:

    """
    return self._state

  @property
  def level(self):
    """

    Returns:

    """
    return self._level
