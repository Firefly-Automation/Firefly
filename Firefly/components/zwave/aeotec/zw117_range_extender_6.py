from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import (EVENT_ACTION_OFF)

TITLE = 'Aeotec ZW117 Range Extender'
DEVICE_TYPE = 'UNKNONW'
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = []
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_switch = ZW117(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_switch.id] = new_switch
  return new_switch.id


class ZW117(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = {}
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self._export_ui = False
