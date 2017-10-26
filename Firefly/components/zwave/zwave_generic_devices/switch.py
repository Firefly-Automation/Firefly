from Firefly import logging
from Firefly.components.zwave.device_types.switch import ZwaveSwitch

TITLE = 'Zwave Switch'


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  switch = Switch(firefly, package, **kwargs)
  return firefly.install_component(switch)


class Switch(ZwaveSwitch):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, **kwargs)
