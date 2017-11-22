from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue
from Firefly.const import AUTHOR, DEVICE_TYPE_THERMOSTAT

from Firefly import logging
from Firefly.helpers.device_types.thermostat import Thermostat
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.helpers.metadata import action_on_off_switch

from Firefly.helpers.device.const import THERMOSTAT, THERMOSTAT_FAN, THERMOSTAT_FAN_AUTO, THERMOSTAT_FAN_ON, \
  THERMOSTAT_MODE, THERMOSTAT_MODE_AUTO, THERMOSTAT_MODE_COOL, THERMOSTAT_MODE_ECO, THERMOSTAT_MODE_HEAT, \
  THERMOSTAT_OFF, THERMOSTAT_TARGET_COOL, THERMOSTAT_TARGET_HEAT, TEMPERATURE

COMMANDS = ['set_fan', THERMOSTAT_FAN_ON, THERMOSTAT_FAN_AUTO]
REQUESTS = [THERMOSTAT_FAN, THERMOSTAT_MODE, THERMOSTAT_TARGET_HEAT, THERMOSTAT_TARGET_COOL, TEMPERATURE]
INITIAL_VALUES = {
  '_mode':        THERMOSTAT_OFF,
  '_target_heat': 55,
  '_target_cool': 85,
  '_fan':         THERMOSTAT_FAN_AUTO
}
CAPABILITIES = {
  THERMOSTAT_MODE_ECO:  False,
  THERMOSTAT_MODE_AUTO: False,
  THERMOSTAT_MODE_HEAT: True,
  THERMOSTAT_MODE_COOL: True,
  THERMOSTAT_OFF:       True
}

FAN_MODE_MAP = {
  THERMOSTAT_FAN_AUTO: 'Auto Low',
  THERMOSTAT_FAN_ON:   'On Low'
}


class ZwaveThermostat(Thermostat, ZwaveDevice):
  def __init__(self, firefly, package, title='Zwave Thermostat', initial_values={}, **kwargs):
    if kwargs.get('commands') is not None:
      commands = kwargs.get('commands')
      kwargs.pop('commands')
    else:
      commands = COMMANDS

    if kwargs.get('requests') is not None:
      requests = kwargs.get('requests')
      kwargs.pop('requests')
    else:
      requests = REQUESTS

    if kwargs.get('capabilities') is not None:
      capabilities = kwargs.get('capabilities')
      kwargs.pop('capabilities')
    else:
      capabilities = CAPABILITIES

    super().__init__(firefly, package, title, AUTHOR, commands, requests, DEVICE_TYPE_THERMOSTAT,
                     capabilities=capabilities, initial_values=initial_values, **kwargs)

  def set_thermostat(self, **kwargs):
    fan_mode = kwargs.get('fan')
    if fan_mode is not None:
      set_fan = FAN_MODE_MAP[fan_mode]
      self.node.set_thermostat_fan_mode(set_fan)

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    logging.info('[THERMOSTAT] %s' % str(kwargs))
    super().update_from_zwave(node, ignore_update, **kwargs)

    label = values.label
    if label == 'Mode':
      self.update_values(mode=values.data)
    if label == 'Heating 1':
      self.update_values(target_heat=values.data)
    if label == 'Cooling 1':
      self.update_values(target_cool=values.data)
    if label == 'Temperature':
      self.update_values(temperature=values.data)
    if label == 'Fan Mode':
      self.update_values(fan=THERMOSTAT_FAN_AUTO if values.data == 'Auto Low' else THERMOSTAT_FAN_ON)
