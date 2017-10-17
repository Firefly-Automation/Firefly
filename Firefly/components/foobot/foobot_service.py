from Firefly import logging, scheduler
import configparser
from Firefly.const import FOOBOT_SECTION, SERVICE_FOOBOT, AUTHOR, SERVICE_CONFIG_FILE
from Firefly.helpers.service import Service
import requests

TITLE = 'Foobot Service'
COMMANDS = []
REQUESTS = []

OWNER_URL = 'http://api.foobot.io/v2/owner/%s/device/'
STATUS_URL = 'http://api.foobot.io/v2/device/%s/datapoint/0/last/0/'

def Setup(firefly, package, **kwargs):
  logging.message('Setting up %s service' % SERVICE_FOOBOT)
  config = configparser.ConfigParser()
  config.read(SERVICE_CONFIG_FILE)
  enable = config.getboolean(FOOBOT_SECTION, 'enable', fallback=False)
  username = config.get(FOOBOT_SECTION, 'username', fallback=None)
  api_key = config.get(FOOBOT_SECTION, 'api_key', fallback=None)
  refresh_interval = config.getint(FOOBOT_SECTION, 'refresh_interval', fallback=15)

  if not enable or not api_key or not username:
    return False

  foobot = Foobot(firefly, package, enable=enable, username=username, api_key=api_key, refresh_interval=refresh_interval, **kwargs)
  firefly.components[SERVICE_FOOBOT] = foobot


class Foobot(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_FOOBOT, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self.enable = kwargs.get('enable', False)
    self.username = kwargs.get('username')
    self.api_key = kwargs.get('api_key')
    self.refresh_interval = kwargs.get('refresh_interval', 15)
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

