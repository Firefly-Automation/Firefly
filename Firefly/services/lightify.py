import configparser
import lightify
from uuid import uuid4
from time import sleep

import requests
import aiohttp

from Firefly import logging, scheduler
from Firefly.const import COMMAND_UPDATE, SERVICE_CONFIG_FILE, AUTHOR
from Firefly.helpers.events import Command
from Firefly.helpers.service import Service

from Firefly.components.lightify import lightify_light

TITLE = 'Lightify Lights'
SERVICE_ID = 'service_lightify'
COMMANDS = ['send_command', 'refresh', 'send_request']
REQUESTS = ['get_lights', 'get_groups']

SECTION = 'LIGHTIFY'


def Setup(firefly, package, **kwargs):
  logging.message('Setting up %s service' % SERVICE_ID)
  config = configparser.ConfigParser()
  config.read(SERVICE_CONFIG_FILE)

  enable = config.getboolean(SECTION, 'enable', fallback=False)
  ip = config.get(SECTION, 'ip', fallback=None)

  if not enable or not ip:
    return False

  lighify = Lightify(firefly, package, enable=enable, ip=ip,  **kwargs)
  firefly.components[SERVICE_ID] = lighify

  return True

class Lightify(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self.ip = kwargs.get('ip')

    self.bridge = lightify.Lightify(self.ip)

    self.refrsh_id = str(uuid4())

    scheduler.runEveryS(10, self.refresh, job_id=self.refrsh_id)




  def refresh(self):
    self.bridge.update_all_light_status()
    self.bridge.update_group_list()

    for ff_id, light in self.bridge.lights().items():
      ff_id = str(ff_id)
      if ff_id in self.firefly.components:
        command = Command(ff_id, SERVICE_ID, COMMAND_UPDATE, lightify_object=light)
        self.firefly.send_command(command)
        continue

      self._firefly.install_package('Firefly.components.lightify.lightify_light', ff_id=ff_id, alias=light.name(), lightify_object=light)




