from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue

from Firefly import logging
from Firefly.components.zwave.device_types.switch import ZwaveSwitch
from Firefly.const import ACTION_OFF, ACTION_ON, SWITCH, LEVEL

TITLE = 'Leviton DZMX1 Dimmer'

BATTERY = 'battery'
ALARM = 'alarm'

COMMANDS = [ACTION_OFF, ACTION_ON, LEVEL]
REQUESTS = [SWITCH, LEVEL]

INITIAL_VALUES = {
  '_state': 'off',
  '_level': -1
}

CAPABILITIES = {
  SWITCH: True,
  LEVEL: True,
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  switch = ZwaveLevitonDimmer(firefly, package, **kwargs)
  firefly.install_component(switch)
  return switch.id


class ZwaveLevitonDimmer(ZwaveSwitch):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs.update({
      'initial_values': INITIAL_VALUES,
      'commands':       COMMANDS,
      'requests':       REQUESTS
    })
    super().__init__(firefly, package, TITLE, capabilities=CAPABILITIES, **kwargs)

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    super().update_from_zwave(node, ignore_update, values, values_only, **kwargs)

    if node is None:
      return

    #try:
    #  if not node.values[self.value_map['Switch']].is_polled:
    #    node.values[self.value_map['Switch']].enable_poll()
    #except:
    #  pass

    try:
      if not node.values[self.value_map['Level']].is_polled:
        node.values[self.value_map['Level']].enable_poll(3)
    except:
      pass
