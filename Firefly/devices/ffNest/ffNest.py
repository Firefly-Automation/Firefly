# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-08-15 21:15:42
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-08-15 21:49:10

import logging

import requests

from core.firefly_api import ffScheduler as Scheduler
from core.models.device import Device


URL = 'https://home.nest.com/user/login'

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Nest Device',
      'type' : 'thermostat',
      'package' : 'ffNest',
      'module' : 'ffNest'
    }
    
    self.COMMANDS = {
      'update' : self.update,
      'setPresence' : self.setPresence,
    }

    self.REQUESTS = {
      'presence' : self.getPresence,
      'state' : self.getState,
      'temp' : self.getTemp
    }

    self.VIEWS = {
      'display' : True,
      'name' : args.get('args').get('name'),
      'id' : deviceID,
      'type' : 'thermostat',
      'dash_view' : {
        'request' : 'temp',
        'type' : 'text', 
        'text' : {
          "false" : {
            'click' : 'true',
            'color' : 'grey',
            'command' : {'presence':True},
            'text' : 'Away'
          },
          "true" : {
            'click' : 'false',
            'color' : 'green',
            'command' : {'presence':False},
            'default' : True,
            'text' : 'Present'
          }
        }
      }
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')
    self._username = args.get('username')
    self._password = args.get('password')
    self._serial = args.get('serial')
    self._f = args.get('f')

    self._auth_data = None
    self._raw_status = None
    self._thermostatOperatingState = None
    self._temp = None

    Scheduler.runEveryM(5,self.update,replace=True,uuid='NEST-UPDATER')

    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################



  def login(self):
    logging.debug("Logging into Nest.")
    data = {
      'username' : self._username,
      'password' : self._password
    }
    self._auth_data = requests.post(URL, data=data).json()

  def status(self):
    logging.debug("Getting nest status.")
    url_base = self._auth_data.get('urls').get('transport_url')
    url = url_base + '/v2/mobile'

    headers = {
      'X-nl-protocol-version': '1',
      'X-nl-user-id': self._auth_data.get('userid'),
      'Authorization': "Basic " + self._auth_data.get('access_token')
    }

    self._raw_status = requests.get(url, headers=headers).json()

    logging.critical(str(self._raw_status))


  def setPresence(self, value):
    return 0


  def getPresence(self):
    return 0

  def getState(self):
    return 0

  def getTemp(self):
    return 0

  def update(self):
    logging.critical('---------UPDATING NEST----------')
    self.login()
    self.status()
    return 0