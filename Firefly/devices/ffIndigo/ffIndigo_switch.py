# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-17 20:28:40
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-08 19:14:03

from core.models.device import Device
from core.services import ffIndigo


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
      'card': "<md-card layout='row' layout-align='center center' layout-wrap><device-card layout='row' flex layout-wrap layout-align='center center'><span  style='cursor: pointer;' ng-click='selectDeviceIndex($index)' layout-align='start center' flex=''> {{::item.name}} </span><md-switch layout-align='end center' ng-model=deviceStates[item.id].on ng-click='switch(!deviceStates[item.id].on)'></md-switch></device-card></div><md-card-content ng-if='$index ==selectedDeviceIndex' flex=100 layout-wrap><md-divider></md-divider><div layout='row' layout-align='center center'><md-button flex=50 ng-click='switch(true)'>On</md-button><md-button flex=50 ng-click='switch(false)'>Off</md-button></div><md-divider></md-divider><md-subhead> Turn off in: </md-subhead> <div layout='row' layout-align='center center'><md-button flex=25>30m</md-button><md-button flex=25>1h</md-button><md-button flex=25>2h</md-button><md-button flex=25>4h</md-button></div><br><md-card-actions layout='row' layout-align='start center' flex='100'><md-button flex=50>More Info</md-button></md-card-actions></md-card-content></md-card>"
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
