import configparser

import nest

from Firefly import logging, scheduler
from Firefly.const import COMMAND_UPDATE, NEST_CACHE_FILE, SERVICE_CONFIG_FILE
from Firefly.helpers.events import Command
from Firefly.helpers.service import Service

TITLE = 'nest service for Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = 'service_nest'
COMMANDS = ['refresh', 'set_nest_auth']
REQUESTS = []

SECTION = 'NEST'


def Setup(firefly, package, **kwargs):
  logging.message('Setting up %s service' % SERVICE_ID)
  config = configparser.ConfigParser()
  config.read(SERVICE_CONFIG_FILE)

  enable = config.getboolean(SECTION, 'enable', fallback=True)
  cache_file = config.get(SECTION, 'cache_file', fallback=NEST_CACHE_FILE)
  client_id = config.get(SECTION, 'client_id', fallback='')
  client_secret = config.get(SECTION, 'client_secret', fallback='')

  newNest = Nest(firefly, package, enable=enable, cache_file=cache_file, client_id=client_id, client_secret=client_secret, **kwargs)
  firefly.components[SERVICE_ID] = newNest

  if not enable:
    return False
  return True


class Nest(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)
    self.firefly = firefly
    self.enable = kwargs.get('enable')
    self.cache_file = kwargs.get('cache_file')
    self.client_id = kwargs.get('client_id')
    self.client_secret = kwargs.get('client_secret')
    self.nest = None

    if self.client_secret != '' and self.client_id != '':
      self.init_nest()

    self.add_command('refresh', self.refresh)
    self.add_command('set_nest_auth', self.set_auth)

    self.refresh()
    scheduler.runEveryM(4, self.refresh)

  def init_nest(self):
    self.nest = nest.Nest(client_id=self.client_id, client_secret=self.client_secret, access_token_cache_file=self.cache_file)
    self.refresh()

  def set_auth(self, **kwargs):
    self.client_id = kwargs.get('client_id')
    self.client_secret = kwargs.get('client_secret')
    auth_code = kwargs.get('code')

    if self.client_id is None or self.client_secret is None or auth_code is None:
      return
    self.nest = nest.Nest(client_id=self.client_id, client_secret=self.client_secret, access_token_cache_file=self.cache_file)
    self.nest.request_token(auth_code)

    config = configparser.ConfigParser()
    config.read(SERVICE_CONFIG_FILE)
    config.set(SECTION, r'client_id', str(self.client_id))
    config.set(SECTION, r'client_secret', str(self.client_secret))
    with open(SERVICE_CONFIG_FILE, 'w') as configfile:
      config.write(configfile)
    logging.info('Config file for hue has been updated.')

    self.refresh()

  def refresh(self, **kwargs):
    logging.info('Refreshing Nest')
    try:
      for t in self.nest.thermostats:
        ff_id = t.serial
        alias = t.name_long
        if ff_id not in self.firefly.components:
          package = 'Firefly.components.nest.thermostat'
          self.firefly.install_package(package, alias=alias, ff_id=ff_id, thermostat=t)
        else:
          self.firefly.send_command(Command(ff_id, SERVICE_ID, COMMAND_UPDATE, thermostat=t))
    except Exception as e:
      # TODO: Generate Error Code
      logging.error(e)

  def refresh_firebase(self):
    refresh_command = Command('service_firebase', 'hue', 'refresh')
    self.firefly.send_command(refresh_command)
