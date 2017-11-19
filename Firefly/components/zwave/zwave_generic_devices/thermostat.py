from Firefly import logging
from Firefly.components.zwave.device_types.thermostat import ZwaveThermostat
from Firefly.const import SWITCH

TITLE = 'Zwave Thermostat'

def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  switch = Thermostat(firefly, package, **kwargs)
  return firefly.install_component(switch)


class Thermostat(ZwaveThermostat):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, **kwargs)
