from uuid import uuid4

import lightify

from Firefly import logging, scheduler
from Firefly.const import AUTHOR, COMMAND_UPDATE
from Firefly.core.service_handler import ServiceConfig, ServicePackage
from Firefly.helpers.events import Command
from Firefly.helpers.service import Service

TITLE = 'Lightify Lights'
SERVICE_ID = 'service_lightify'
COMMANDS = ['send_command', 'refresh', 'send_request']
REQUESTS = ['get_lights', 'get_groups']

SECTION = 'LIGHTIFY'


def Setup(firefly, package, alias, ff_id, service_package: ServicePackage, config: ServiceConfig, **kwargs):
  logging.info('Setting up %s service' % service_package.name)
  lighify = Lightify(firefly, alias, ff_id, service_package, config, **kwargs)
  firefly.install_component(lighify)
  return True


class Lightify(Service):
  def __init__(self, firefly, alias, ff_id, service_package: ServicePackage, config: ServiceConfig, **kwargs):
    # TODO: Fix this
    package = service_package.package
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)
    self.config = config
    self.ip = config.ip

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
      else:
        self._firefly.install_package('Firefly.components.lightify.lightify_light', ff_id=ff_id, alias=light.name(), lightify_object=light)

    for name, group in self.bridge.groups().items():
      ff_id = 'lightify-group-%s' % name.replace(' ', '_')
      if ff_id in self.firefly.components:
        command = Command(ff_id, SERVICE_ID, COMMAND_UPDATE, lightify_object=group, lightify_bridge=self.bridge)
        self.firefly.send_command(command)
      else:
        self._firefly.install_package('Firefly.components.lightify.lightify_group', ff_id=ff_id, alias=name, lightify_object=group, lightify_bridge=self.bridge)
