import json
from Firefly import logging


DEFAULT_ON_COMMAND = {"set_light":{"level": 100, "switch": "on", "ct":6500}}
DEFAULT_ALARM_COMMAND = "alarm1"

class AlarmSettings(object):
  def __init__(self, lights=[], on_command=DEFAULT_ON_COMMAND, alarms=[], alarm_on_command=DEFAULT_ALARM_COMMAND, **kwargs):
    self.lights = lights
    self.on_command = on_command
    self.alarms = alarms
    self.alarm_on_command = alarm_on_command



class FireflySecuritySettings(object):
  def __init__(self, config_file='dev_config/security_settings.json'):
    self.file_path = config_file
    self.config = {}

    self.alarm_config = AlarmSettings()

    self._secure_motion_modes = ['away', 'vacation', 'alarm']
    self._secure_no_motion_modes = ['night']


  def load_config(self):
    with open(self.file_path, 'rb') as config_file:
      self.config = json.load(config_file)

    alarm_settings = self.config.get('alarm')
    self.alarm_config = AlarmSettings(**alarm_settings)

    self._secure_motion_modes = self.config.get('secure_motion_enabled', ['away', 'vacation', 'alarm'])
    self._secure_no_motion_modes = self.config.get('secure_motion_disabled', ['night'])


  def save_config(self):
    logging.info('[FIREFLY SECURITY] saving config')
    with open(self.file_path, 'w') as config_file:
      config = self.alarm_config.__dict__
      config['secure_motion_enabled'] = self._secure_motion_modes
      config['secure_motion_disabled'] = self._secure_no_motion_modes
      json.dump(config, config_file, indent=4, sort_keys=True)


  @property
  def lights(self):
    return self.alarm_config.lights

  @property
  def light_command(self):
    return self.alarm_config.on_command

  @property
  def alarms(self):
    return self.alarm_config.alarms

  @property
  def alarm_command(self):
    return self.alarm_config.alarm_on_command

  @property
  def secure_modes_motion(self):
    return self._secure_motion_modes

  @property
  def secure_modes_no_motion(self):
    return self._secure_no_motion_modes



