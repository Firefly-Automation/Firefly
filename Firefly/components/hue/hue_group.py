from Firefly import logging
from Firefly.components.hue.hue_device import HueDevice
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import (ACTION_LEVEL, ACTION_OFF, ACTION_ON, ACTION_TOGGLE, DEVICE_TYPE_SWITCH, EVENT_ACTION_OFF, LEVEL, STATE, SWITCH)

TITLE = 'Firefly Hue Group'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ACTION_LEVEL]
REQUESTS = [STATE, LEVEL, SWITCH, 'hue', 'sat']
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF
}


def Setup(firefly, package, **kwargs):
  """

  Args:
      firefly:
      package:
      kwargs:
  """
  logging.message('Entering %s setup' % TITLE)
  # TODO: Remove this in the future
  kwargs['tags'] = ['light']
  hue_group = HueGroup(firefly, package, **kwargs)
  firefly.install_component(hue_group)
  return hue_group.id


class HueGroup(HueDevice):
  """
  """

  def __init__(self, firefly, package, **kwargs):
    """

    Args:
        firefly:
        package:
        kwargs:
    """
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    if kwargs.get('initial_values'):
      self.__dict__.update(kwargs['initial_values'])
