# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-08-15 21:15:42
# @Last Modified by:   Zachary Priddy


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
      'home' : self.setHome,
      'away' : self.setAway,
      'setTarget' : self.setTarget
    }

    self.REQUESTS = {
      'presence' : self.getPresence,
      'state' : self.getState,
      'temp' : self.getTemp,
      'target' : self.getTargetTemp,
      'fan' : self.getFan,
      'targetType' : self.getTargetType
    }


    self.VIEWS = {
      'display' : True,
      'name' : args.get('args').get('name'),
      'id' : deviceID,
      'type' : 'thermostat',
      'card' : "<md-card ><div layout='row'  layout-align='center center'><device-card layout='row' flex layout-wrap layout-align='center center'><span flex layout='row'><md-title layout-align='center center' style='cursor: pointer;' ng-click='selectDeviceIndex($index)'>{{ item.name }}</md-title></span><md-card-content layout-align='center center' style='padding:7px' layout='row'><md-button><ng-md-icon icon='expand_more'></ng-md-icon></md-button><span layout-align='center center' style='font-size:20px'>{{deviceStates[item.id].current}}</span><md-button><ng-md-icon icon='expand_less'></ng-md-icon></md-button></div></device-card><md-card-content ng-show='$index ==selectedDeviceIndex'><md-divider></md-divider><div layout='row' layout-align='center center' layout-wrap><md-button flex=50>On</md-button><md-button flex=50>Off</md-button></div><md-divider></md-divider><md-subhead> Turn off in: </md-subhead> <div layout='row' layout-align='center center'><md-button flex=25>30m</md-button><md-button flex=25>1h</md-button><md-button flex=25>2h</md-button><md-button flex=25>4h</md-button></div><br><md-card-actions layout='row' layout-align='start center'><md-button>More Info</md-button></md-card-actions></md-card-content></md-card-content></md-card>",
      'target' : self.getTemp(), 
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
    logging.critical("Logging into Nest.")
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

    shared = self.shared

    if shared is not None:
      self._hvac_ac_state = shared.get('hvac_ac_state')
      self._hvac_heater_state = shared.get('hvac_heater_state')
      self._hvac_fan_state = shared.get('hvac_fan_state')
      self._target_temperature_type = shared.get('target_temperature_type')
      self._target_temperature = shared.get('target_temperature')
      self._target_temperature_high = shared.get('target_temperature_high')
      self._target_temperature_low = shared.get('target_temperature_low')
      self._nest_auto_away = shared.get('auto_away')




  def setHome(self, args={}):
    logging.critical('SET HOME')
    return self.setPresence(value=True)

  def setAway(self, args={}):
    return self.setPresence(value=False)

  def setPresence(self, value=True):
    logging.critical('SET NEST TO ' + str(value))
    
    try:
      presence = not value

      self.login()

      url_base = self._auth_data.get('urls').get('transport_url')
      url = url_base + '/v2/put/structure.' + self._structure_id

      headers = {
        "user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
        'X-nl-protocol-version': '1',
        'X-nl-user-id': self._auth_data.get('userid'),
        'Authorization': "Basic " + self._auth_data.get('access_token')
      }

      data = {
        'away' : presence
      }

      r = requests.post(url, headers=headers, json=data)

      return True
      
    except:
      return False

  def setTarget(self, args={}):
    target = args.get('target')
    logging.critical('-------------SET NEST TARGET TO: ' + str(target))
    try:
      self.login()

      url_base = self._auth_data.get('urls').get('transport_url')
      url = url_base + '/v2/put/shared.' + self._serial

      headers = {
        "user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
        'X-nl-protocol-version': '1',
        'X-nl-user-id': self._auth_data.get('userid'),
        'Authorization': "Basic " + self._auth_data.get('access_token')
      }

      data = {
        'target_temperature' : target
      }

      r = requests.post(url, headers=headers, json=data)

      return True
      
    except:
      return False


  def getTargetType(self, args={}):
    return self._target_temperature_type


  def getPresence(self, args={}):
    try:
      presence = not self.structure.get('away')
      return presence
    except:
      return 0

  def getState(self, args={}):
    try:
      if self.getPresence() is False:
        if self._hvac_ac_state is True:
          self._thermostatOperatingState = "awaycool"
        elif self._hvac_heater_state is True:
          self._thermostatOperatingState = "awayheat"
        else:
          self._thermostatOperatingState = "awayidle"
      else:
        if self._hvac_ac_state is True:
          self._thermostatOperatingState = "cool"
        elif self._hvac_heater_state is True:
          self._thermostatOperatingState = "heat"
        else:
          self._thermostatOperatingState = "idle"

      return self._thermostatOperatingState
    except:
      return 0

  def getTemp(self, args={}):
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
            'value' : str(self._temp) + ' (away)'
          },
          "awayidle" : {
            'click' : 'true',
            'color' : 'grey',
            'command' : 'update',
            'value' : str(self._temp) + ' (away)'
          },
          "awaycool" : {
            'click' : 'false',
            'color' : 'blue',
            'command' : 'update',
            'default' : True,
            'value' : str(self._temp) + ' (away)'
          },
          "awayheat" : {
            'click' : 'false',
            'color' : 'red',
            'command' : 'update',
            'default' : True,
            'value' : str(self._temp) + ' (away)'
          }
        }
      }, 
      'card' : "<md-card ><div layout='row'  layout-align='center center'><device-card layout='row' flex layout-wrap layout-align='center center'><span flex layout='row'><md-title layout-align='center center' style='cursor: pointer;' ng-click='selectDeviceIndex($index)'>{{ item.name }}</md-title></span><md-card-content layout-align='center center' style='padding:7px' layout='row'><md-button><ng-md-icon icon='expand_more' ng-click='setTarget(deviceStates[item.id].views.status.target-1.0)'></ng-md-icon></md-button><span layout-align='center center' style='font-size:20px'>{{deviceStates[item.id].views.status.current}}</span><md-button><ng-md-icon icon='expand_less' ng-click='setTarget(deviceStates[item.id].views.status.target-1.0)'></ng-md-icon></md-button></div></device-card><md-card-content ng-show='$index ==selectedDeviceIndex'><md-divider></md-divider><div layout='row' layout-align='center center' layout-wrap><md-button flex=50>On</md-button><md-button flex=50>Off</md-button></div><md-divider></md-divider><md-subhead> Turn off in: </md-subhead> <div layout='row' layout-align='center center'><md-button flex=25>30m</md-button><md-button flex=25>1h</md-button><md-button flex=25>2h</md-button><md-button flex=25>4h</md-button></div><br><md-card-actions layout='row' layout-align='start center'><md-button>More Info</md-button></md-card-actions></md-card-content></md-card-content></md-card>",
      'status' : {
        'current' : self._temp,
        'target' : self._target_temperature,
        'high' : self._target_temperature_high,
        'low' : self._target_temperature_low
        } 
    }

    self.refreshData()
    return 0

  @property
  def shared(self):
    if self._raw_status is not None:
      return self._raw_status.get('shared').get(self._serial)
    return None

  @property
  def structure(self):
    try:
      return self._raw_status.get('structure').get(self._structure_id)
    except:
      return None
  

def c2f(celsius):
  return float("{0:.1f}".format((celsius * 1.8) + 32))