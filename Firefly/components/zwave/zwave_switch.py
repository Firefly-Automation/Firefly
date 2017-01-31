from Firefly import logging
from Firefly.helpers.device import Device
from Firefly.util.get_from_kwargs import get_kwargs_value

from openzwave.network import ZWaveNode
from Firefly import logging
from Firefly.const import (STATE_OFF, STATE_ON, ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON,
                           ACTION_TOGGLE, DEVICE_TYPE_SWITCH, SENSORS)



TITLE = 'Firefly Zwave Switch'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, 'ZWAVE_CONFIG']
REQUESTS = [STATE, 'SENSORS', 'PARAMS', 'DEVICE_VALUES']
INITIAL_VALUES = {'_state': STATE_OFF}

def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_switch = ZwaveSwitch(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_switch.id] = new_switch
  return new_switch.id


class ZwaveSwitch(Device):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self._sensors = {}
    self._config_params = {}
    self._device_values = {}

    self._node = kwargs.get('node')
    if self._node:
      self._switches = list(self._node.get_switches().keys())

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)
    self.add_command('ZWAVE_CONFIG', self.zwave_config)

    self.add_request(STATE, self.get_state)
    self.add_request('SENSORS', self.get_sensors)
    self.add_request('PARAMS', self.get_params)
    self.add_request('DEVICE_VALUES', self.get_device_values)


  def off(self, **kwargs):
    self._state = STATE_OFF
    print(self._switches)
    self._node.set_switch(self._switches[0], 0)
    return EVENT_ACTION_OFF

  def on(self, **kwargs):
    self._state = STATE_ON
    self._node.set_switch(self._switches[0], 1)
    return EVENT_ACTION_ON

  def zwave_config(self, **kwargs):
    param = int(get_kwargs_value(kwargs, 'id'))
    value = int(get_kwargs_value(kwargs, 'value'))
    self._node.set_config_param(param, value)

  def get_sensors(self, **kwargs):
    print(kwargs)
    sensor = get_kwargs_value(kwargs, 'SENSOR')
    if sensor:
      s = self._sensors.get(sensor)
      return s
    return self._sensors

  def get_params(self, **kwargs):
    print(kwargs)
    values = get_kwargs_value(kwargs, 'VALUE')
    if values:
      s = self._config_params.get(values)
      return s
    return self._config_params

  def get_device_values(self, **kwargs):
    return self._device_values


  def toggle(self, **kwargs):
    if self.state == STATE_ON:
      return self.off()
    return self.on()

  def get_state(self, **kwargs):
    return self.state

  def update_from_zwave(self, node: ZWaveNode, **kwargs):
    for s, i in node.get_sensors().items():
      self._sensors[SENSORS.get(i.label)] = i.data

    for s, i in node.get_values().items():
      if i.command_class == 112:
        self._config_params[i.label.upper()] = {'value': i.data, 'id': i.index}
      else:
        self._device_values[i.label.upper()] = {'value': i.data, 'id': i.index, 'class': i.command_class}

    if node.get_switch_state(self._switches[0]):
      self._state = STATE_ON
    else:
      self._state = STATE_OFF

    self._node = node.get

  @property
  def state(self):
    return self._state
