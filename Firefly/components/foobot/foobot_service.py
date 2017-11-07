from Firefly import logging, scheduler
import configparser
from Firefly.const import FOOBOT_SECTION, SERVICE_FOOBOT, AUTHOR, SERVICE_CONFIG_FILE
from Firefly.helpers.service import Service
from Firefly.core.service_handler import ServiceConfig, ServicePackage
import requests

TITLE = 'Foobot Service'
COMMANDS = []
REQUESTS = []

OWNER_URL = 'http://api.foobot.io/v2/owner/%s/device/'
STATUS_URL = 'http://api.foobot.io/v2/device/%s/datapoint/0/last/0/'

def Setup(firefly, package, alias, ff_id, service_package: ServicePackage, config: ServiceConfig, **kwargs):
  logging.info('Setting up %s service' % service_package.name)
  foobot = Foobot(firefly, alias, ff_id, service_package, config, **kwargs)
  firefly.install_component(foobot)
  return True


class Foobot(Service):
  def __init__(self, firefly, alias, ff_id, service_package: ServicePackage, config: ServiceConfig, **kwargs):
    # TODO: Fix this
    package = service_package.package
    super().__init__(firefly, SERVICE_FOOBOT, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self.config = config
    self.enable = config.enabled
    self.username = config.username
    self.api_key = config.api_key
    self.refresh_interval = config.refresh
    self.devices = []


    self.get_devices()
    scheduler.runEveryH(2, self.get_devices, job_id='foobot_discovery')


  def get_devices(self):
    headers = {
      'X-API-KEY-TOKEN': self.api_key
    }
    r = requests.get(OWNER_URL%self.username, headers=headers, timeout=10)
    if r.status_code != 200:
      logging.notify('Foobot Error: %s' % str(r.text))
      return
    self.devices = r.json()
    self.install_devices()

  def install_devices(self):
    for device in self.devices:
      ff_id = str(device.get('uuid'))
      if not ff_id:
        continue
      if ff_id not in self.firefly.components:
        package = 'Firefly.components.foobot.foobot'
        self.firefly.install_package(package, alias=device.get('name'), ff_id=ff_id, foobot_info=device, api_key=self.api_key, username=self.username, refresh_interval=self.refresh_interval)

