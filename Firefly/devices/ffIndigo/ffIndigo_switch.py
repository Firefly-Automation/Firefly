# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-17 20:28:40
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-08 19:14:03

from core.models.device import Device
from core.services import ffIndigo
from core.templates import ffTemplates


class Device(Device):
  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title': 'Firefly Infigo Light Device',
      'type': 'switch',
      'package': 'ffIndigo',
      'module': 'ffIndigo_light'
    }

    self.COMMANDS = {
      'on': self.setOn,
      'off': self.setOff,
      'switch': self.switch,
      'update': self.update
    }

    self.REQUESTS = {
      'on': self.getOn,
    }

    self.VIEWS = {
      'display': True,
      'name': args.get('args').get('name'),
      'id': deviceID,
      'type': 'lights',
      'dash_view': {
        'request': 'on',
        'type': 'switch',
        'switch': {
          "false": {
            'command': {'switch': 'off'},
            'text': 'Off'
          },
          "true": {
            'command': {'switch': 'on'},
            'default': True,
            'text': 'On'
          }
        }
      },
      'card': ffTemplates.switch
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')
    self._name = args.get('name')
    self._type = args.get('type')
    self._rest_url = args.get('restURL')
    self._on = args.get('isOn')
    self._display_in_ui = args.get('displayInUI')


    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device, self).__init__(deviceID, name)
    ###########################
    ###########################

  ####################### START OF DEVICE CODE #############################

  @property
  def on(self):
    return self._on

  @property
  def rest_url(self):
    return self._rest_url

  def setOff(self, args={}):
    self._on = False
    return self.set_light({'isOn': self.on})

  def setOn(self, args={}):
    self._on = True
    return self.set_light({'isOn': self.on})

  def getOn(self):
    return self.on

  def switch(self, value):
    if value == 'on':
      self._on = True
    elif value == 'off':
      self._on = False
    return self.set_light({'isOn': self.on})


  def set_light(self, command):
    ffIndigo.send_command(self.rest_url, command)

  def update(self, raw_data):
    self._on = raw_data.get('isOn')
