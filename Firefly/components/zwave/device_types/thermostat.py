from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue
from Firefly.const import AUTHOR, DEVICE_TYPE_THERMOSTAT

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.helpers.metadata import action_on_off_switch

MODE = "mode"
HEAT = "heat"
COOL = "cool"
OFF = 'off'
FAN_ON = 'fan_on'
FAN_AUTO = 'fan_off'
SET_HEAT = 'set_heat'
SET_COOL = 'set_cool'
FAN = 'fan'
HEAT_TEMP = 'heat_temp'
COOL_TEMP = 'cool_temp'


COMMANDS = [MODE, HEAT, COOL, OFF, FAN_ON, FAN_OFF, SET_HEAT, SET_COOL]

REQUESTS = [FAN, HEAT_TEMP, COOL_TEMP]

CAPABILITIES = {

}

INITIAL_VALUES = {
  '_fan_state': 'off'
}

class ZwaveThermostat(ZwaveDevice):
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

    super().__init__(firefly, package, title, AUTHOR, commands, requests, DEVICE_TYPE_THERMOSTAT, capabilities=capabilities, initial_values=initial_values, **kwargs)


    self.add_request(FAN, self.get_fan)

    self.add_command(FAN_ON, self.fan_on)
    self.add_command(FAN_AUTO, self.fan_auto)

    self.add_action(FAN, action_on_off_switch(False, 'Fan Mode', 'Set fan to On or Auto', FAN, FAN_ON, FAN_AUTO))


  def get_fan(self, **kwargs):
    self._fan_state = 'on' if self.node.get_thermostat_state() == 'On Low' else 'off'
    return self._fan_state

  def fan_on(self, **kwargs):
    self.node.set_thermostat_fan_mode('On Low')

  def fan_off(self, **kwargs):
    self.node.set_thermostat_fan_mode('Auto Low')

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    logging.info('[THERMOSTAT] %s' % str(kwargs))
    super().update_from_zwave(node, ignore_update, **kwargs)

    try:
      self._fan_state = 'on' if self.node.get_thermostat_state() == 'On Low' else 'off'
    except:
      pass