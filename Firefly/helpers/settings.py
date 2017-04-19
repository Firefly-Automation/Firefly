import configparser

from Firefly.const import (FIREFLY_CONFIG_SECTION, CONFIG_HOST, CONFIG_PORT, CONFIG_DEFAULT_HOST, CONFIG_DEFAULT_PORT,
                           CONFIG_POSTAL_CODE, CONFIG_MODES, CONFIG_MODES_DEFAULT)


class Settings(object):
  def __init__(self, config_file):
    self.config = configparser.ConfigParser()
    self.config.read(config_file)

  @property
  def firefly_port(self):
    return self.config.getint(FIREFLY_CONFIG_SECTION, CONFIG_PORT, fallback=CONFIG_DEFAULT_PORT)

  @property
  def firefly_host(self):
    return self.config.get(FIREFLY_CONFIG_SECTION, CONFIG_HOST, fallback=CONFIG_DEFAULT_HOST)

  # TODO: Write modes setter for saving new modes
  @property
  def modes(self):
    modes = self.config.get(FIREFLY_CONFIG_SECTION, CONFIG_MODES, fallback=CONFIG_MODES_DEFAULT)
    modes = [m.strip() for m in modes.split(',')]
    return modes

  @property
  def postal_code(self):
    return self.config.get(FIREFLY_CONFIG_SECTION, CONFIG_POSTAL_CODE, fallback=None)
