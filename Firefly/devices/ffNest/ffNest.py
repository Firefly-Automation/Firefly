# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-08-15 21:15:42
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-08-16 14:45:30

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
      'startup' : self.update,
    }

    self.REQUESTS = {
      'presence' : self.getPresence,
      'state' : self.getState,
      'temp' : self.getTemp,
      'target' : self.getTargetTemp,
      'fan' : self.getFan
    }


    self.VIEWS = {
      'display' : True,
      'name' : args.get('args').get('name'),
      'id' : deviceID,
      'type' : 'thermostat',
      'dash_view' : {
        'request' : 'state',
        'type' : 'stateValue', 
        'state' : {
          "idle" : {
            'click' : 'true',
            'color' : 'grey',
            'command' : 'update',
            'value' : self.getTemp()
          },
          "cool" : {
            'click' : 'false',
            'color' : 'blue',
            'command' : 'update',
            'default' : True,
            'value' : self.getTemp()
          },
          "heat" : {
            'click' : 'false',
            'color' : 'red',
            'command' : 'update',
            'default' : True,
            'value' : self.getTemp()
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
    self._structure_id = None

    self._hvac_ac_state = None
    self._hvac_heater_state = None
    self._hvac_fan_state = None
    self._target_temperature_type = None
    self._target_temperature = None
    self._target_temperature_high = None
    self._target_temperature_low = None
    self._auto_away = None




    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################

    self.update()


  def login(self, args={}):
    logging.debug("Logging into Nest.")
    data = {
      'username' : self._username,
      'password' : self._password
    }
    self._auth_data = requests.post(URL, data=data).json()

  def status(self, args={}):
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

    self.update_shared()

  def update_shared(self, args={}):
    try:
      shared = self.shared

      self._hvac_ac_state = shared.get('hvac_ac_state')
      self._hvac_heater_state = shared.get('hvac_heater_state')
      self._hvac_fan_state = shared.get('hvac_fan_state')
      self._target_temperature_type = shared.get('target_temperature_type')
      self._target_temperature = shared.get('target_temperature')
      self._target_temperature_high = shared.get('target_temperature_high')
      self._target_temperature_low = shared.get('target_temperature_low')
      self._nest_auto_away = shared.get('auto_away')
    except:
      pass



  def setPresence(self, value):
    return 0


  def getPresence(self, args={}):
    try:
      presence = self.structure.get('away')
      logging.critical('Nest Presence : (away)' + str(presence))
      return presence
    except:
      return 0

  def getState(self, args={}):
    try:
      if self._hvac_ac_state is True:
        self._thermostatOperatingState = "cool"
      elif self._hvac_heater_state is True:
        self._thermostatOperatingState = "heat"
      else:
        self._thermostatOperatingState = "idle"

      logging.critical('Nest State: ' + str(self._thermostatOperatingState))
      return self._thermostatOperatingState
    except:
      return 0

  def getTemp(self, args={}):
    logging.critical('Getting TEMP')
    try:
      temp = self.shared.get('current_temperature')
      if self._f:
        temp = c2f(temp)
      logging.critical('Nest TEMP: ' + str(temp))
      self._temp = temp
      return temp
    except:
      return 0

  def getFan(self, args={}):
    return self._hvac_fan_state

  def getTargetTemp(self, args={}):
    try:
      if self._f:
        return {
          'target' : c2f(self._target_temperature),
          'high' : c2f(self._target_temperature_high),
          'low' : c2f(self._target_temperature_low)
          }
      else:
        return {
          'target' : self._target_temperature,
          'high' : self._target_temperature_high,
          'low' : self._target_temperature_low
          }
    except:
      return 0

  def update(self, args={}):
    logging.critical('---------UPDATING NEST----------')
    self.login()
    self.status()

    self.VIEWS = {
      'display' : True,
      'name' : self.name,
      'id' : self.id,
      'type' : 'thermostat',
      'dash_view' : {
        'request' : 'state',
        'type' : 'stateValue', 
        'state' : {
          "idle" : {
            'click' : 'true',
            'color' : 'grey',
            'command' : 'update',
            'value' : self._temp
          },
          "cool" : {
            'click' : 'false',
            'color' : 'blue',
            'command' : 'update',
            'default' : True,
            'value' : self._temp
          },
          "heat" : {
            'click' : 'false',
            'color' : 'red',
            'command' : 'update',
            'default' : True,
            'value' : self._temp
          }
        }
      }
    }

    self.refreshData()
    return 0

  @property
  def shared(self):
    logging.critical('GETTING SHARED ---------------- NEST')
    if self._raw_status is not None:
      return self._raw_status.get(self._serial).get('shared')
    logging.critical('RAW STATUS IS NONE!')
    return None

  @property
  def structure(self):
    try:
      return self._raw_status.get('structure').get(self._structure_id)
    except:
      return None
  

def c2f(celsius):
  return (celsius * 1.8) + 32