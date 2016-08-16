# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-08-15 21:15:42
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-08-15 22:35:12

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
      'startup' : self.refresh_scheduler,
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
        'request' : 'state',
        'type' : 'text', 
        'text' : {
          "false" : {
            'click' : 'true',
            'color' : 'grey',
            'command' : {},
            'text' : str(self._temp)
          },
          "true" : {
            'click' : 'false',
            'color' : 'blue',
            'command' : {},
            'default' : True,
            'text' : str(self._temp)
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
    self._structure = None,
    self._structure_id = None

    self.refresh_scheduler()


    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################


  def refresh_scheduler(self):
    logging.critical('------NEST STARTUP-----')
    Scheduler.runEveryM(5,self.update,replace=True,uuid='NEST-UPDATER')


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
    url = url_base + '/v2/mobile/user.' + self._auth_data.get('userid')

    headers = {
      'X-nl-protocol-version': '1',
      'X-nl-user-id': self._auth_data.get('userid'),
      'Authorization': "Basic " + self._auth_data.get('access_token')
    }

    self._raw_status = requests.get(url, headers=headers).json()

    self._structure_id = self._raw_status.get('structure').keys()[0]
    self._structure = self._raw_status.get('structure').get(self._structure_id)


  def setPresence(self, value):
    return 0


  def getPresence(self):
    try:
      presence = self._structure.get('away')
      logging.critical('Nest Presence : (away)' + str(presence))
      return presence
    except:
      return 0

  def getState(self):
    try:
      self._thermostatOperatingState = self._raw_status.get('shared').get(self._serial).get('hvac_ac_state')
      logging.critical('Nest State: ' + str(self._thermostatOperatingState))
      return self._thermostatOperatingState
    except:
      return 0

  def getTemp(self):
    try:
      temp = self._raw_status.get('shared').get(self._serial).get('current_temperature')
      if self._f:
        temp = c2f(temp)
      logging.critical('Nest TEMP: ' + str(temp))
      return temp
    except:
      return 0

  def update(self):
    logging.critical('---------UPDATING NEST----------')
    self.login()
    self.status()
    self.refreshData()
    return 0

def c2f(celsius):
  return (celsius * 1.8) + 32