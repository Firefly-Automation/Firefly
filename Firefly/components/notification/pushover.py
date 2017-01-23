from Firefly import logging
from Firefly.helpers.device import Device
from Firefly.const import (DEVICE_TYPE_NOTIFICATION, AUTHOR, COMMAND_NOTIFY, SERVICE_NOTIFICATION, PRIORITY_EMERGENCY, PRIORITY_HIGH, PRIORITY_NORMAL, PRIORITY_LOW)

import requests


TITLE = 'Firefly Pushover Device (pushover.net)'
DEVICE_TYPE = DEVICE_TYPE_NOTIFICATION
AUTHOR = AUTHOR
COMMANDS = [COMMAND_NOTIFY]
REQUESTS = []
INITIAL_VALUES = {}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  api_key = kwargs.get('api_key')
  user_key = kwargs.get('user_key')

  if api_key is None or user_key is None:
    return False

  pushover = Pushover(firefly, package, api_key=api_key, user_key=user_key, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[pushover.id] = pushover

  # We are going to use the hard-coded link_device function of the notification service here.
  firefly.components[SERVICE_NOTIFICATION].link_device(pushover.id)
  return True


class Pushover(Device):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self._api_key = kwargs.get('api_key')
    self._user_key = kwargs.get('user_key')

    self.add_command(COMMAND_NOTIFY, self.send)

  def send(self, **kwargs):
    message = kwargs.get('message')
    if message is None:
      return False
    priority = kwargs.get('priority') if kwargs.get('priority') else PRIORITY_NORMAL
    device = kwargs.get('device')
    title = 'Firefly Notification' if not kwargs.get('title') else kwargs.get('title')

    post_data = {
      'token': self._api_key,
      'user': self._user_key,
      'title': title,
      'priority': priority,
      'message': message
    }

    if device is not None:
      post_data['device'] = device

    # TODO: handel response and emergency types of notifications
    requests.post('https://api.pushover.net/1/messages.json', data=post_data)
