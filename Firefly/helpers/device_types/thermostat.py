from Firefly import logging
from Firefly.helpers.device.const import THERMOSTAT, THERMOSTAT_FAN, THERMOSTAT_FAN_AUTO, THERMOSTAT_FAN_ON, \
  THERMOSTAT_MODE, THERMOSTAT_MODE_AUTO, THERMOSTAT_MODE_COOL, THERMOSTAT_MODE_ECO, THERMOSTAT_MODE_HEAT, \
  THERMOSTAT_OFF, THERMOSTAT_TARGET_COOL, THERMOSTAT_TARGET_HEAT, TEMPERATURE
from Firefly.helpers.device.device import Device
from Firefly.helpers.metadata import action_switch, action_text

COMMANDS = ['set_thermostat', 'set_mode', 'set_fan']
REQUESTS = [THERMOSTAT_FAN, THERMOSTAT_MODE, THERMOSTAT_TARGET_HEAT, THERMOSTAT_TARGET_COOL, TEMPERATURE]
INITIAL_VALUES = {
  '_mode':        THERMOSTAT_OFF,
  '_target_heat': 55,
  '_target_cool': 85,
  '_fan':         THERMOSTAT_FAN_AUTO,
  '_temperature': -1,
  '_units':       'F'
}
CAPABILITIES = {
  THERMOSTAT_MODE_ECO:  False,
  THERMOSTAT_MODE_AUTO: False,
  THERMOSTAT_MODE_HEAT: True,
  THERMOSTAT_MODE_COOL: True,
  THERMOSTAT_OFF:       True
}


class Thermostat(Device):
  def __init__(self, firefly, package, title, author, commands=COMMANDS, requests=REQUESTS,
               device_type=THERMOSTAT, capabilities=CAPABILITIES, initial_values=INITIAL_VALUES, **kwargs):
    logging.message('SETTING UP THERMOSTAT')

    INITIAL_VALUES.update(initial_values)
    initial_values = INITIAL_VALUES

    CAPABILITIES.update(capabilities)
    capabilities = CAPABILITIES

    self.capabilities = capabilities

    super().__init__(firefly, package, title, author, commands, requests, device_type, initial_values=initial_values,
                     **kwargs)

    # Build the modes that are compatible with the thermostat
    self.modes = [mode for mode, compatible_mode in self.capabilities.items() if compatible_mode]

    self.add_command('set_thermostat', self.set_thermostat)
    self.add_command('set_mode', self.set_mode)
    self.add_command('set_fan', self.set_fan)

    self.add_request(THERMOSTAT_FAN, self.get_fan)
    self.add_request(THERMOSTAT_MODE, self.get_mode)
    self.add_request(TEMPERATURE, self.get_temperature)
    self.add_action(TEMPERATURE,
                    action_text(primary=True, context='Current Temperature', title='Temperature', request=TEMPERATURE,
                                units=self._units))

    self.add_command(THERMOSTAT_FAN_ON, self.set_fan_on)
    self.add_command(THERMOSTAT_FAN_AUTO, self.set_fan_auto)
    self.add_action(THERMOSTAT_FAN,
                    action_switch(True, True, False, 'Fan', 'Change fan mode', THERMOSTAT_FAN, THERMOSTAT_FAN_ON,
                                  THERMOSTAT_FAN_AUTO))

    if self.capabilities[THERMOSTAT_MODE_COOL]:
      self.add_command(THERMOSTAT_MODE_COOL, self.set_cool)
      self.add_command(THERMOSTAT_TARGET_COOL, self.set_target_cool)
      self.add_request(THERMOSTAT_TARGET_COOL, self.get_target_cool)
      # TODO: Add action for setting target_cool

    if self.capabilities[THERMOSTAT_MODE_HEAT]:
      self.add_command(THERMOSTAT_MODE_HEAT, self.set_heat)
      self.add_command(THERMOSTAT_TARGET_HEAT, self.set_target_heat)
      self.add_request(THERMOSTAT_TARGET_HEAT, self.get_target_heat)
      # TODO: Add action for setting target_heat

    if self.capabilities[THERMOSTAT_OFF]:
      self.add_command(THERMOSTAT_OFF, self.set_off)

    if self.capabilities[THERMOSTAT_MODE_AUTO]:
      self.add_command(THERMOSTAT_MODE_AUTO, self.set_auto)

    if self.capabilities[THERMOSTAT_MODE_ECO]:
      self.add_command(THERMOSTAT_MODE_ECO, self.set_eco)

  def get_temperature(self, **kwargs):
    return self._temperature

  def set_thermostat(self, **kwargs):
    logging.warn('Not Implemented')

  def set_target_heat(self, target_temp, **kwargs):
    """ Set the heat target temperature

    :param target_temp: temperature to set for heating
    :param kwargs:
    """
    self.set_thermostat(target_high=target_temp)

  def get_target_heat(self, **kwargs):
    return self._target_heat

  def set_target_cool(self, target_temp, **kwargs):
    """ Set the cool target temperature

    :param target_temp: temperature to set for cooling
    :param kwargs:
    """
    self.set_thermostat(target_coolw=target_temp)

  def get_target_cool(self, **kwargs):
    return self._target_cool

  def set_mode(self, mode, **kwargs):
    if mode in self.modes:
      self.set_thermostat(mode=mode, **kwargs)

  def set_off(self, **kwargs):
    self.set_mode(THERMOSTAT_OFF, **kwargs)

  def set_cool(self, **kwargs):
    self.set_mode(THERMOSTAT_MODE_COOL, **kwargs)
    if kwargs.get('target_cool'):
      self.set_target_cool(kwargs.get('target_cool'))

  def set_heat(self, **kwargs):
    self.set_mode(THERMOSTAT_MODE_HEAT, **kwargs)
    if kwargs.get('target_heat'):
      self.set_target_heat(kwargs.get('target_heat'))

  def set_eco(self, **kwargs):
    self.set_mode(THERMOSTAT_MODE_ECO)

  def set_auto(self, **kwargs):
    self.set_mode(THERMOSTAT_MODE_AUTO)

  def get_mode(self, **kwargs):
    return self._mode

  def set_fan(self, fan, **kwargs):
    if fan in [THERMOSTAT_FAN_ON, THERMOSTAT_MODE_AUTO]:
      self.set_thermostat(fan=fan)
      return
    if type(fan) is bool:
      self.set_thermostat(fan=(THERMOSTAT_FAN_ON if fan else THERMOSTAT_FAN_AUTO))
      return
    logging.warn('[THERMOSTAT] %s fan mode not supported' % str(fan))

  def set_fan_on(self, **kwargs):
    self.set_fan(THERMOSTAT_FAN_ON)

  def set_fan_auto(self, **kwargs):
    self.set_fan(THERMOSTAT_FAN_AUTO)

  def get_fan(self, **kwargs):
    return self._fan

  def update_values(self, mode=None, fan=None, target_heat=None, target_cool=None, temperature=None, **kwargs):
    # self.store_state_before()

    if mode is not None:
      self._mode = mode

    if temperature is not None:
      try:
        self._temperature = float(temperature)
      except:
        logging.error('[THERMOSTAT] error parsing temperature')

    if fan is not None:
      if type(fan) is bool:
        self._fan = THERMOSTAT_FAN_ON if fan else THERMOSTAT_FAN_AUTO
      elif fan in [THERMOSTAT_FAN_AUTO, THERMOSTAT_FAN_ON]:
        self._fan = fan
      else:
        logging.warn('[THERMOSTAT] fan mode not supported: %s' % fan)

    if target_cool is not None:
      try:
        target_cool = float(target_cool)
        self._target_cool = target_cool
      except:
        logging.error('[THERMOSTAT] error parsing target_cool: %s' % target_cool)

    if target_heat is not None:
      try:
        target_heat = int(target_heat)
        self._target_heat = target_heat
      except:
        logging.error('[THERMOSTAT] error parsing target_heat: %s' % target_heat)
