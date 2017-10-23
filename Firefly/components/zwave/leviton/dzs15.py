from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue

from Firefly import logging
from Firefly.components.zwave.device_types.switch import ZwaveSwitch
from Firefly.const import ACTION_OFF, ACTION_ON, SWITCH

TITLE = 'Leviton DZS 15 Switch'

BATTERY = 'battery'
ALARM = 'alarm'
POWER_METER = 'power_meter'
VOLTAGE_METER = 'voltage_meter'

CURRENT = 'power_current'
CURRENT_ENERGY_READING = 'current_energy_reading'
PREVIOUS_ENERGY_READING = 'previous_energy_reading'
VOLTAGE = 'voltage'
WATTS = 'watts'

COMMANDS = [ACTION_OFF, ACTION_ON]
REQUESTS = [SWITCH]

INITIAL_VALUES = {}

CAPABILITIES = {
  SWITCH: True,
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  switch = ZwaveLevitonSwitch(firefly, package, **kwargs)
  firefly.install_component(switch)
  return switch.id


class ZwaveLevitonSwitch(ZwaveSwitch):
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

    if not node.values[self.value_map['Switch']].is_polled:
      node.values[self.value_map['Switch']].enable_poll()
