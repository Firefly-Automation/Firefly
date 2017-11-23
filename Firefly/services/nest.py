import configparser

import nest

from Firefly import logging, scheduler
from Firefly.const import COMMAND_UPDATE, NEST_CACHE_FILE, SERVICE_CONFIG_FILE
from Firefly.helpers.events import Command
from Firefly.helpers.service import Service

from Firefly.core.service_handler import ServicePackage, ServiceConfig

TITLE = 'nest service for Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = 'service_nest'
COMMANDS = ['refresh', 'set_nest_auth']
REQUESTS = []

SECTION = 'NEST'


def Setup(firefly, package, alias, ff_id, service_package:ServicePackage, config:ServiceConfig, **kwargs):
  logging.info('Setting up %s service' % service_package.name)
  newNest = Nest(firefly, alias, ff_id, service_package, config, **kwargs)
  firefly.install_component(newNest)
  return True


class Nest(Service):
  def __init__(self, firefly, alias, ff_id, service_package:ServicePackage, config:ServiceConfig, **kwargs):
    #TODO: Fix this
    package = service_package.package
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)
    self.config = config
    self.enable = config.enabled
    self.cache_file = service_package.config['cache']
    self.access_token = config.access_token
    self.nest = None

    if self.access_token:
      self.init_nest()

    self.add_command('refresh', self.refresh)
    self.add_command('set_nest_auth', self.set_auth)

    self.refresh()
    scheduler.runEveryM(4, self.refresh, job_id='Nest Refresh')

  def init_nest(self):
    self.nest = nest.Nest(access_token=self.access_token, access_token_cache_file=self.cache_file)
    self.refresh()

  def set_auth(self, **kwargs):
    logging.info('setting nest auth')
    self.access_token = kwargs.get('access_token')

    if self.access_token is None:
      return
    self.nest = nest.Nest(access_token=self.access_token, access_token_cache_file=self.cache_file)

    self.config.access_token = self.access_token
    self.config.save()
    logging.info('Config file for nest has been updated.')

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
