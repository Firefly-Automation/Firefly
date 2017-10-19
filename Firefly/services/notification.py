from Firefly import logging
from Firefly.helpers.service import Service
from Firefly.helpers.events import Command
from Firefly.const import COMMAND_NOTIFY, SERVICE_NOTIFICATION, NOTIFY_DEFAULT, PRIORITY_NORMAL
import asyncio
'''
Notification service may have its own config file to save device mappings into
'''


TITLE = 'Notification Service Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = SERVICE_NOTIFICATION
COMMANDS = [COMMAND_NOTIFY, 'add_default', 'remove_default', ] # TODO: Add actions like cancel for pushover
REQUESTS = ['default_list']


def Setup(firefly, package, **kwargs):
  notify = Notify(firefly, package, **kwargs)
  firefly.install_component(notify)


class Notify(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    # TODO: maybe read and write this to config file for services
    self._default = []
    self._devices = []

    self.add_command(COMMAND_NOTIFY, self.send)
    self.add_command('add_default', self.add_default)
    self.add_command('remove_default', self.remove_default)

    self.add_request('default_list', self.get_default_list)


  def send(self, **kwargs):
    message = kwargs.get('message')
    device = kwargs.get('device', NOTIFY_DEFAULT)
    priority = kwargs.get('priority', PRIORITY_NORMAL)
    if message is None:
      return False

    if device == NOTIFY_DEFAULT:
      device = self._default if len(self._default) > 0 else self._devices
    if type(device) is str:
      device = [device]

    for d in device:
      notify_command = Command(d, SERVICE_ID, COMMAND_NOTIFY, priority=priority, **kwargs)
      self._firefly.send_command(notify_command)

    if self._firefly.components.get('service_firebase'):
      self._firefly.components['service_firebase'].push_notification(message, priority)

    return True


  def add_default(self, ff_id, **kwargs):
    self._default.append(ff_id)
    return True

  def remove_default(self, ff_id, **kwargs):
    if ff_id not in self._default:
      return False
    self._default.remove(ff_id)
    return True

  def get_default_list(self, **kwargs):
    return self._default

  def link_device(self, ff_id, **kwargs):
    print('link device %s' % ff_id)
    self._devices.append(ff_id)


