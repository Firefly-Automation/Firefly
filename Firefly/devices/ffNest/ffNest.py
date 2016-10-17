# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-08-15 21:15:42
# @Last Modified by:   Zachary Priddy


import logging

from core.models.device import Device


class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title': 'Firefly Nest Device',
      'type': 'thermostat',
      'package': 'ffNest',
      'module': 'ffNest'
    }

    self.COMMANDS = {
      'update': self.update,
      'setPresence': self.setPresence,
      'startup': self.update,
      'home': self.setHome,
      'away': self.setAway,
      'setTarget': self.setTarget
    }

    self.REQUESTS = {
      'presence': self.getPresence,
      'state': self.getState,
      'temp': self.getTemp,
      'target': self.getTargetTemp,
      'fan': self.getFan,
      'targetType': self.getTargetType
    }

    self.VIEWS = {
      'display': True,
      'name': args.get('args').get('name'),
      'id': deviceID,
      'type': 'thermostat',
      'card': "<md-card ><div layout='row'  layout-align='center center'><device-card layout='row' flex layout-wrap layout-align='center center'><span flex layout='row'><md-title layout-align='center center' style='cursor: pointer;' ng-click='selectDeviceIndex($index)'>{{ item.name }}</md-title></span><md-card-content layout-align='center center' style='padding:7px' layout='row'><md-button><ng-md-icon icon='expand_more'></ng-md-icon></md-button><span layout-align='center center' style='font-size:20px'>{{deviceStates[item.id].current}}</span><md-button><ng-md-icon icon='expand_less'></ng-md-icon></md-button></div></device-card><md-card-content ng-show='$index ==selectedDeviceIndex'><md-divider></md-divider><div layout='row' layout-align='center center' layout-wrap><md-button flex=50>On</md-button><md-button flex=50>Off</md-button></div><md-divider></md-divider><md-subhead> Turn off in: </md-subhead> <div layout='row' layout-align='center center'><md-button flex=25>30m</md-button><md-button flex=25>1h</md-button><md-button flex=25>2h</md-button><md-button flex=25>4h</md-button></div><br><md-card-actions layout='row' layout-align='start center'><md-button>More Info</md-button></md-card-actions></md-card-content></md-card-content></md-card>"
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')
    self._where = args.get('where')
    self._label = args.get('label')

    if self._where:
      self._where = self._where.lower()

    if self._label:
      self._label = self._label.lower()

    self._structure = args.get('structure_name')
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

    # new
    self._away = False
    self._device_index = None

    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device, self).__init__(deviceID, name)
    ###########################
    ###########################

    self.update()

  def startup(self, args={}):
    self.update()

  def status(self, args={}):
    logging.debug("Getting nest status.")
    self.getState()

  def setHome(self, args={}):
    logging.critical('SET NEST TO HOME')
    return self.setPresence(value=True)

  def setAway(self, args={}):
    logging.critical('SET NEST TO AWAY')
    return self.setPresence(value=False)

  def setPresence(self, value=True):
    settings = {'away': value}
    self.setNest(settings)

  def setTarget(self, args={}):
    target = args.get('target')
    settings = {'target': float(target)}
    self.setNest(settings)

  def getTargetType(self, args={}):
    return self._target_temperature_type

  def getPresence(self, args={}):
    return self._away

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
    return self._temp

  def getFan(self, args={}):
    return self._hvac_fan_state

  def getTargetTemp(self, args={}):
    return {
        'target': self._target_temperature,
        'high': self._target_temperature_high,
        'low': self._target_temperature_low
      }

  def setNest(self, settings):
    from core import ffNestModule
    from nest import utils as nest_utils

    self.deviceIndex(ffNestModule)
    structure = ffNestModule.structures[0]
    device = ffNestModule.devices[self._device_index]

    setting_options = settings.keys()

    if 'away' in setting_options:
      structure.away = settings['away']

    if 'target' in setting_options:
      if self._f:
        device.target = nest_utils.f_to_c(settings['target'])
      else:
        device.target = settings['target']

  def getStatus(self):
    from core import ffNestModule
    from nest import utils as nest_utils

    logging.critical('*************************** NEST GET STATUS **********************************')

    self.deviceIndex(ffNestModule)
    structure = ffNestModule.structures[0]

    # TODO: This isnt working yet. This needs to use the same logic as above.
    if self._structure:
      structure = ffNestModule.structures[self._structure]
    self._away = structure.away

    device = ffNestModule.devices[self._device_index]

    self._temp = device.temperature
    if self._f:
      self._temp = nest_utils.c_to_f(self._temp)

    if device.mode == 'range':
      self._target_temperature_low, self._target_temperature_high = device.target
    else:
      self._target_temperature = device.target

    self._target_temperature_type = device.mode
    self._hvac_fan_state = device.fan


  def deviceIndex(self, ffNestModule):
    if not self._device_index:
      for idx, d in enumerate(ffNestModule.devices):
        if self._where:
          if d.where.lower() == self._where:
            self._device_index = idx
        if self._label:
          if d.name.lower() == self._label:
            self._device_index = idx

    return self._device_index

  def update(self, args={}):
    logging.critical('*************************** NEST UPDATE **********************************')

    self.getStatus()

    self.VIEWS = {
      'display': True,
      'name': self.name,
      'id': self.id,
      'type': 'thermostat',
      'card': "<md-card ><div layout='row'  layout-align='center center'><device-card layout='row' flex layout-wrap layout-align='center center'><span flex layout='row'><md-title layout-align='center center' style='cursor: pointer;' ng-click='selectDeviceIndex($index)'>{{ item.name }}</md-title></span><md-card-content layout-align='center center' style='padding:7px' layout='row'><md-button><ng-md-icon icon='expand_more' ng-click='setTarget(deviceStates[item.id].views.status.target-1.0)'></ng-md-icon></md-button><span layout-align='center center' style='font-size:20px'>{{deviceStates[item.id].views.status.current}}</span><md-button><ng-md-icon icon='expand_less' ng-click='setTarget(deviceStates[item.id].views.status.target+1.0)'></ng-md-icon></md-button></div></device-card><md-card-content ng-show='$index ==selectedDeviceIndex'><md-divider></md-divider><div layout='row' layout-align='center center' layout-wrap><md-button flex=50>On</md-button><md-button flex=50>Off</md-button></div><md-divider></md-divider><md-subhead> Turn off in: </md-subhead> <div layout='row' layout-align='center center'><md-button flex=25>30m</md-button><md-button flex=25>1h</md-button><md-button flex=25>2h</md-button><md-button flex=25>4h</md-button></div><br><md-card-actions layout='row' layout-align='start center'><md-button>More Info</md-button></md-card-actions></md-card-content></md-card-content></md-card>",
      'status': {
        'current': self._temp,
        'target': self._target_temperature,
        'high': self._target_temperature_high,
        'low': self._target_temperature_low
      }
    }

    self.refreshData()
    return 0
