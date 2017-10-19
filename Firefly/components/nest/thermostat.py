from Firefly import logging
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import (COMMAND_UPDATE, DEVICE_TYPE_THERMOSTAT, LEVEL)
from Firefly.helpers.action import Command
from Firefly.helpers.device import Device
from Firefly.helpers.metadata import metaButtonObject, metaButtons, metaSlider, metaText
from Firefly import scheduler
from uuid import uuid4

# TODO(zpriddy): Add more delayed setters to help with rate limits.

TITLE = 'Nest Thermostat'
DEVICE_TYPE = DEVICE_TYPE_THERMOSTAT
AUTHOR = AUTHOR
COMMANDS = [COMMAND_UPDATE, LEVEL, 'temperature', 'mode', 'away', 'home']
REQUESTS = ['temperature', 'humidity', 'mode', 'away', 'target']
INITIAL_VALUES = {
  '_temperature': -1,
  '_humidity':    -1,
  '_target':      -1,
  '_mode':        'unknown',
  '_away':        'unknown'
}

MODE_LIST = ['off', 'eco', 'cool', 'heat', 'heat-cool']


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  thermostat = Thermostat(firefly, package, **kwargs)
  firefly.install_component(thermostat)

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
    self.add_command('away', self.set_away)
    self.add_command('home', self.set_home)

    self.add_request('temperature', self.get_temperature)
    self.add_request('target', self.get_target)
    self.add_request('humidity', self.get_humidity)
    self.add_request('mode', self.get_mode)
    self.add_request('away', self.get_away)

    self.add_action('temperature', metaSlider(min=50, max=90, request_param='target', set_command='temperature', command_param='temperature', title='Target Temperature'))
    self.add_action('current_temperature', metaText(title='Current Temperature', text_request='temperature', primary=True))
    eco_button = metaButtonObject('Eco', 'mode', 'mode', 'eco')
    heat_button = metaButtonObject('Heat', 'mode', 'mode', 'heat')
    cool_button = metaButtonObject('Cool', 'mode', 'mode', 'cool')
    off_button = metaButtonObject('Off', 'mode', 'mode', 'off')
    # TODO: Enable range when supported
    # range_button = metaButtonObject('Range ', 'mode', 'mode', 'off')
    buttons = [eco_button, cool_button, heat_button, off_button]
    self.add_action('mode_buttons', metaButtons(title='AC Modes', buttons=buttons, request_val='mode', context='Change AC Mode'))

    # Buttons for Home/Away
    home_button = metaButtonObject('Home', 'away', 'away', 'home')
    away_button = metaButtonObject('Away', 'away', 'away', 'away')
    self.add_action('home_away_buttons', metaButtons(title='Home Mode (nest)', buttons=[home_button, away_button], request_val='away', context='Set Nest to Home/Away'))

    self._alexa_export = False
    self.timer_id = str(uuid4())

  def get_temperature(self, **kwargs):
    return self.temperature

  def get_target(self, **kwargs):
    return self.target

  def get_humidity(self, **kwargs):
    return self.humidity

  def get_mode(self, **kwargs):
    return self.mode

  def get_away(self, **kwargs):
    return self.away

  def set_away(self, **kwargs):
    '''set_away will set to away by default, if 'away' is in kwargs it will set to the value of 'away'
    '''
    away = kwargs.get('away')
    if away is None:
      away = 'away'
    if away not in ['away', 'home']:
      return
    self.away = away

  def set_home(self, **kwargs):
    self.away = 'home'

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
      self._temperature = value
      scheduler.runInS(5, self.set_temperature_delayed, job_id=self.timer_id, temperature=value)
    else:
      logging.error('thermostat not set yet')

  def set_temperature_delayed(self, temperature=None):
    """Set the mode after a 5 second delay. This helps with rate limiting.

    Args:
      mode: mode to be set to.
    """
    if temperature is not None:
      try:
        self.thermostat.temperature = temperature
      except Exception as e:
        logging.error('Error setting thermostat temperature: %s' % e)


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
      self._mode = value
      scheduler.runInS(5, self.set_mode_delayed, job_id=self.timer_id, mode=value)
    else:
      logging.error('thermostat not set yet')

  def set_mode_delayed(self, mode=None):
    """Set the mode after a 5 second delay. This helps with rate limiting.

    Args:
      mode: mode to be set to.
    """
    if mode is not None:
      try:
        self.thermostat.mode = mode
      except Exception as e:
        logging.error('Error setting thermostat mode: %s' % e)


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

  @property
  def target(self):
    if self.thermostat:
      self._target = self.thermostat.target
    return self._target
