from Firefly import logging
from Firefly.const import ACTION_OFF, ACTION_ON, COMMAND_SET_LIGHT, DEVICE_TYPE_SWITCH, LEVEL, SWITCH
from Firefly.helpers.device import COLOR, COLOR_TEMPERATURE, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_BRI, COLOR_HEX, COLOR_HUE, COLOR_SAT
from Firefly.helpers.device.device import Device
from Firefly.helpers.metadata.metadata import action_dimmer, action_on_off_switch
from Firefly.services.alexa.alexa_const import ALEXA_LIGHT, ALEXA_POWER_INTERFACE, ALEXA_POWER_LEVEL_INTERFACE, ALEXA_COLOR_INTERFACE, ALEXA_COLOR_TEMPERATURE_INTERFACE
from Firefly.util.color import populate_colors, Colors

ALARM = 'alarm'
POWER_METER = 'power_meter'
VOLTAGE_METER = 'voltage_meter'

CURRENT = 'power_current'
CURRENT_ENERGY_READING = 'current_energy_reading'
PREVIOUS_ENERGY_READING = 'previous_energy_reading'
VOLTAGE = 'voltage'
WATTS = 'watts'

COMMANDS = [ACTION_OFF, ACTION_ON, LEVEL, COMMAND_SET_LIGHT]

REQUESTS = [SWITCH, LEVEL]

CAPABILITIES = {
  LEVEL:             False,
  SWITCH:            False,
  COLOR:             False,
  COLOR_TEMPERATURE: False,
  COMMAND_SET_LIGHT: True
}

INITIAL_VALUES = {
  '_level':     -1,
  '_switch':    ACTION_OFF,
  '_min_level': -1,
  '_ct':        -1,
  '_r':         -1,
  '_g':         -1,
  '_b':         -1,
  '_hue':       -1,
  '_sat':       -1,
  '_bri':       -1,
  '_hex':       -1
}


class Light(Device):
  def __init__(self, firefly, package, title, author, commands=COMMANDS, requests=REQUESTS, device_type=DEVICE_TYPE_SWITCH, capabilities=CAPABILITIES, initial_values=INITIAL_VALUES, **kwargs):
    logging.message('SETTING UP SWITCH')

    initial_values_updated = INITIAL_VALUES.copy()
    initial_values_updated.update(initial_values)
    initial_values = initial_values_updated

    capabilities_updated = CAPABILITIES.copy()
    capabilities_updated.update(capabilities)
    capabilities = capabilities_updated

    super().__init__(firefly, package, title, author, commands, requests, device_type, initial_values=initial_values, **kwargs)

    self.add_alexa_categories(ALEXA_LIGHT)

    if capabilities[SWITCH] and SWITCH in requests and ACTION_OFF in commands and ACTION_ON in commands:
      self.add_command(ACTION_OFF, self.set_off)
      self.add_command(ACTION_ON, self.set_on)
      self.add_request(SWITCH, self.get_switch)

      self.add_alexa_capabilities(ALEXA_POWER_INTERFACE)

      self.add_action(SWITCH, action_on_off_switch())

    if capabilities[LEVEL] and LEVEL in requests and LEVEL in commands:
      self.add_request(LEVEL, self.get_level)
      self.add_command(LEVEL, self.set_level)

      self.add_action(LEVEL, action_dimmer())
      self.add_alexa_capabilities(ALEXA_POWER_LEVEL_INTERFACE)

    if capabilities[COMMAND_SET_LIGHT] and COMMAND_SET_LIGHT in commands:
      self.add_command(COMMAND_SET_LIGHT, self.parent_set_light)


    if capabilities[COLOR]:
      self.add_request(COLOR_RED, self.get_red)
      self.add_request(COLOR_GREEN, self.get_green)
      self.add_request(COLOR_BLUE, self.get_blue)
      self.add_request(COLOR_HEX, self.get_hex)
      self.add_request(COLOR_HUE, self.get_hue)
      self.add_request(COLOR_SAT, self.get_sat)
      self.add_request(COLOR_BRI, self.get_bri)

      self.add_alexa_capabilities(ALEXA_COLOR_INTERFACE)

    if capabilities[COLOR_TEMPERATURE]:
      self.add_request(COLOR_TEMPERATURE, self.get_ct)

      self.add_alexa_capabilities(ALEXA_COLOR_TEMPERATURE_INTERFACE)


    self._alexa_export = True

    self.capabilities = capabilities

    # TODO: Use device settings for this
    self._security_monitoring = kwargs.get('security_monitoring', True)

  def update_values(self, level=None, switch=None, ct=None, **kwargs):
    logging.info('[LIGHT] Updating Values: %s' % str(kwargs))
    if switch is not None:
      if type(switch) is bool:
        self._switch = ACTION_ON if switch else ACTION_OFF
      elif type(switch) is int:
        if switch == 0:
          self._switch = ACTION_OFF
        else:
          self._switch = ACTION_ON
      else:
        self._switch = switch

    if ct is not None:
      self._ct = ct

    if level is not None:
      if type(level) is not int:
        self._level = -1

      # Fix rounding errors for 100%
      if level == 99:
        level = 100

      self._level = level

    colors = populate_colors(**kwargs)
    if colors.is_set:
      self._hex = colors.hex
      self._hue = colors.hue
      self._sat = colors.sat
      self._bri = colors.bri
      self._r = colors.r
      self._g = colors.g
      self._b = colors.b


  def get_red(self, **kwargs):
    return self._r

  def get_green(self, **kwargs):
    return self._g

  def get_blue(self, **kwargs):
    return self._b

  def get_hex(self, **kwargs):
    return self._hex

  def get_switch(self, **kwargs):
    return self._switch

  def get_level(self, **kwargs):
    return self._level

  def get_ct(self, **kwargs):
    return self._ct

  def get_hue(self, **kwargs):
    return self._hue

  def get_sat(self, **kwargs):
    return self._sat

  def get_bri(self, **kwargs):
    return self._bri

  def set_level(self, level=-1, **kwargs):
    if level != -1:
      self.parent_set_light(level=level)

  def set_switch(self, switch=None, **kwargs):
    if switch is not None:
      self.parent_set_light(switch=switch)

  def parent_set_light(self, **kwargs):
    """ parent_set_light takes all the set_light params and if there are colors converts the colors into other formats

    Args:
      **kwargs:
    """
    colors = populate_colors(**kwargs)
    kwargs['colors'] = colors

    if kwargs.get('level'):
      try:
        kwargs['level'] = int(kwargs['level'])
      except:
        kwargs['level'] = 100

    self.set_light(**kwargs)

  def set_light(self, switch=None, level=None, colors=Colors(), ct=None, **kwargs):
    logging.error('set_light not implemented.')

  def set_on(self, **kwargs):
    return self.set_switch(ACTION_ON)

  def set_off(self, **kwargs):
    return self.set_switch(ACTION_OFF)
