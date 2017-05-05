from Firefly import logging
from Firefly.components.hue.hue_device import HueDevice
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import ACTION_LEVEL, ACTION_OFF, ACTION_ON, ACTION_TOGGLE, DEVICE_TYPE_SWITCH, LEVEL, STATE, SWITCH

TITLE = 'Firefly Hue Light'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ACTION_LEVEL]
REQUESTS = [STATE, LEVEL, SWITCH]


def Setup(firefly, package, **kwargs):
  """

  Args:
      firefly:
      package:
      kwargs:
  """
  logging.message('Entering %s setup' % TITLE)
  hue_light = HueLight(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[hue_light.id] = hue_light


class HueLight(HueDevice):
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
