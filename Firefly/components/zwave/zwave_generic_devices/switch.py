from Firefly import logging
from Firefly.components.zwave.device_types.switch import ZwaveSwitch
from Firefly.const import SWITCH

TITLE = 'Zwave Switch'

CAPABILITIES = {
  SWITCH:      True,
}

def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  switch = Switch(firefly, package, **kwargs)
  return firefly.install_component(switch)


class Switch(ZwaveSwitch):
  def __init__(self, firefly, package, **kwargs):
    kwargs['capabilities'] = CAPABILITIES
    super().__init__(firefly, package, TITLE, **kwargs)
