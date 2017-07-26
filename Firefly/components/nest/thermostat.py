from Firefly import logging
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import (COMMAND_UPDATE, DEVICE_TYPE_THERMOSTAT, LEVEL)
from Firefly.helpers.action import Command
from Firefly.helpers.device import Device
from Firefly.helpers.metadata import metaButtonObject, metaButtons, metaSlider, metaText

TITLE = 'Nest Thermostat'
DEVICE_TYPE = DEVICE_TYPE_THERMOSTAT
AUTHOR = AUTHOR
COMMANDS = [COMMAND_UPDATE, LEVEL, 'temperature', 'mode']
REQUESTS = ['temperature', 'humidity', 'mode', 'away']
INITIAL_VALUES = {
  '_temperature': -1,
  '_humidity':    -1,
  '_mode':        'unknown',
  '_away':        'unknown'
}

MODE_LIST = ['off', 'eco', 'cool', 'heat', 'heat-cool']


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  thermostat = Thermostat(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[thermostat.id] = thermostat

  refresh_command = Command('service_firebase', 'nest', 'refresh')
  firefly.send_command(refresh_command)


class Thermostat(Device):
  """ Nest Thermostat device.
  """

  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values'):
      INITIAL_VALUES.update(kwargs.get('initial_values'))
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self.thermostat = kwargs.get('thermostat')

    self.add_command(COMMAND_UPDATE, self.update_thermostat)
    self.add_command('temperature', self.set_temperature)
    self.add_command('mode', self.set_mode)
    # TODO: Enable away command.
    # self.add_command('away', self.set_away )

    self.add_request('temperature', self.get_temperature)
    self.add_request('humidity', self.get_humidity)
    self.add_request('mode', self.get_mode)
    self.add_request('away', self.get_away)

    self.add_action('temperature', metaSlider(min=50, max=90, primary=True, request_param='temperature', set_command='temperature', command_param='temperature', title='Target Temperature'))
    self.add_action('away', metaText(title='Nest Home Status', text_request='away'))
    eco_button = metaButtonObject('Eco', 'mode', 'mode', 'eco')
    heat_button = metaButtonObject('Heat', 'mode', 'mode', 'heat')
    cool_button = metaButtonObject('Cool', 'mode', 'mode', 'cool')
    off_button = metaButtonObject('Off', 'mode', 'mode', 'off')
    # TODO: Enable range when supported
    # range_button = metaButtonObject('Range ', 'mode', 'mode', 'off')
    buttons = [eco_button, cool_button, heat_button, off_button]
    self.add_action('mode_buttons', metaButtons(title='AC Modes', buttons=buttons, request_val='mode', context='Change AC Mode'))

    self._alexa_export = False

  def get_temperature(self, **kwargs):
    return self.temperature

  def get_humidity(self, **kwargs):
    return self.humidity

  def get_mode(self, **kwargs):
    return self.mode

  def get_away(self, **kwargs):
    return self.away

  def set_temperature(self, **kwargs):
    t = kwargs.get('temperature')
    if t is None:
      return
    try:
      t = int(t)
    except:
      return
    self.temperature = t

  def set_mode(self, **kwargs):
    m = kwargs.get('mode')
    if m is None:
      logging.error('no mode provided')
      return
    m = m.lower()
    if m not in MODE_LIST:
      logging.error('Invalid Mode')
      return
    self.mode = m

  def update_thermostat(self, **kwargs):
    thermostat = kwargs.get('thermostat')
    if thermostat is not None:
      self.thermostat = thermostat

  @property
  def temperature(self):
    if self.thermostat:
      self._temperature = self.thermostat.temperature
    return self._temperature

  @temperature.setter
  def temperature(self, value):
    if self.thermostat:
      self.thermostat.temperature = value
      self._temperature = value
    else:
      logging.error('thermostat not set yet')

  @property
  def humidity(self):
    if self.thermostat:
      self._humidity = self.thermostat.humidity
    return self._humidity

  @property
  def mode(self):
    if self.thermostat:
      self._mode = self.thermostat.mode
    return self._mode

  @mode.setter
  def mode(self, value):
    if self.thermostat:
      self.thermostat.mode = value
      self._mode = value
    else:
      logging.error('thermostat not set yet')

  @property
  def away(self):
    if self.thermostat:
      self._away = self.thermostat.structure.away
    return self._away

  @away.setter
  def away(self, value):
    if self.thermostat:
      self.thermostat.structure.away = value
      self._away = value
    else:
      logging.error('thermostat not set yet')
