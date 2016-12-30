from core import ffServices
from core import ffScheduler
from core.models.command import Command
import requests
from requests.auth import HTTPDigestAuth
import logging
from devices.ffIndigo.ffIndigo_switch import Device as indigoSwitch

class IndigoService(object):
  def __init__(self):
    self._config = ffServices.get_service_config('INDIGO')
    self._host = self.config.get('host')
    self._port = self.config.get('port')
    self._user = self.config.get('user')
    self._pass = self.config.get('password')
    self._https = ffServices.get_boolean('INDIGO', 'https')
    self._devices = self.get_devices()

    self.install_devices()
    ffScheduler.runEveryS(10, self.refresh_devices)

  @property
  def config(self):
    return self._config

  @property
  def host(self):
    return self._host

  @property
  def port(self):
    return self._port

  @property
  def user(self):
    return self._user

  @property
  def password(self):
    return self._pass

  @property
  def https(self):
    return self._https

  @property
  def url(self):
    if self.https:
      return 'https://%s:%s' % (self.host, self.port)
    return 'http://%s:%s' % (self.host, self.port)

  @property
  def devices(self):
    return self._devices

  def get_devices(self):
    '''
    Gets all devices and configs from Indigo.

    Returns:
      devices (dict): A dict of all devices from Indigo

    '''
    devices = {}
    url = self.url + '/devices.json/'
    device_list = requests.get(url,auth=HTTPDigestAuth(self.user, self.password)).json()

    for d in device_list:
      url = self.url + d.get('restURL')
      ff_name = 'indigo-%s' % d.get('name')
      devices[ff_name] = requests.get(url,auth=HTTPDigestAuth(self.user, self.password)).json()
      devices[ff_name]['restURL'] = d.get('restURL')

    return devices

  def refresh_devices(self):
    self._devices = self.get_devices()
    for name, device in self.devices.iteritems():
      Command(name,{'update': device})

  def send_command(self, device_url, command):
    '''Sends command to Indigo

    Args:
      device_url (str): Device restURL.
      command (dict): Command to be sent i.e {"isOn": 1}

    Returns:
      success (bool): Was command successful. (response code 200)

    '''
    url = self.url + device_url
    r = requests.put(url, data=command)
    return r.status_code == requests.codes.ok

  def install_devices(self):
    '''
    Installs all supported devices from indigo. Each device name will be: indigo-{{NAME}}

    '''
    # TODO Updated this to the enw install_child function
    from core.firefly_api import install_child_device
    for name, device in self.get_devices().iteritems():
      logging.info('Installing child device %s' % name)
      if device.get('typeSupportsOnOff') and not device.get('typeIsSensor') and not device.get('typeIsDimmer'):
        logging.info('SUPPORTED DEVICE')
        config  = {'args': device}
        new_switch = indigoSwitch(name, args=config)
        install_child_device(name, new_switch,config=config)
      else:
        logging.error('UNSUPPORTED DEVICE %s' % name)


      
  







