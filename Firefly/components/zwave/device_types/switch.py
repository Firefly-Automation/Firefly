from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import ACTION_OFF, ACTION_ON, AUTHOR, DEVICE_TYPE_MOTION, LEVEL, SWITCH, DEVICE_TYPE_SWITCH
from Firefly.helpers.device_types.switch import Switch

from Firefly.util.zwave_command_class import COMMAND_CLASS_SWITCH_MULTILEVEL, COMMAND_CLASS_METER

BATTERY = 'battery'
ALARM = 'alarm'
POWER_METER = 'power_meter'
VOLTAGE_METER = 'voltage_meter'

CURRENT = 'power_current'
CURRENT_ENERGY_READING = 'current_energy_reading'
PREVIOUS_ENERGY_READING = 'previous_energy_reading'
VOLTAGE = 'voltage'
WATTS = 'watts'

COMMANDS = [ACTION_OFF, ACTION_ON, LEVEL]

REQUESTS = [ALARM, BATTERY, SWITCH, CURRENT, VOLTAGE, WATTS, LEVEL ]

CAPABILITIES = {
  ALARM:       False,
  BATTERY:     False,
  LEVEL:       False,
  POWER_METER: False,
  SWITCH:      False,
}

INITIAL_VALUES = {
  '_alarm':                   False,
  '_battery':                 -1,
  '_current':                 -1,
  '_current_energy_reading':  -1,
  '_level':                   -1,
  '_previous_energy_reading': -1,
  '_switch':                  ACTION_OFF,
  '_voltage':                 -1,
  '_watts':                   -1
}

class ZwaveSwitch(Switch, ZwaveDevice):
  def __init__(self, firefly, package, title='Zwave Switch', initial_values={}, **kwargs):
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

    super().__init__(firefly, package, title, AUTHOR, commands, requests, DEVICE_TYPE_SWITCH, capabilities=capabilities, initial_values=initial_values, **kwargs)

    self.value_map = {}

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    if node is None:
      return

    self._node = node

    super().update_from_zwave(node, **kwargs)

    if values is None:
      logging.message('ZWAVE SWITCH SENSOR NO VALUES GIVEN')
      return

    label = values.label
    if label == 'Switch':
      self.update_values(switch=values.data)
      self.value_map[values.label] = values.value_id

    if label == 'Battery Level':
      self.update_values(battery=values.data)
      self.value_map[values.label] = values.value_id

    if values.command_class == COMMAND_CLASS_METER:
      self.value_map[values.label] = values.value_id
      if label == 'Energy':
        self.update_values(current_energy_reading=values.data)
      if label == 'Previous Reading':
        self.update_values(previous_energy_reading=values.data)
      if label == 'Power':
        self.update_values(watts=values.data)
      if label == 'Voltage':
        self.update_values(voltage=values.data)

    if label== 'Level' and values.command_class == COMMAND_CLASS_SWITCH_MULTILEVEL:
      self.update_values(level=values.data)


  def set_switch(self, switch=None, **kwargs):
    if switch is None:
      return

    if self.value_map.get('Switch') is None:
      return

    switch_id = self.value_map['Switch']

    on = switch == ACTION_ON
    self._node.set_switch(switch_id, on)
