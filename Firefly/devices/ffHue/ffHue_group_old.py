# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-12 00:03:27
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-13 00:29:20

from core.firefly_api import send_event
from core.models.event import Event as ffEvent
from core.models.command import Command as ffCommand

import logging

metadata = {
  'module' : 'ffHue_group'
}


class Device(object):
  def __init__(self, raw_data, bridgeID, group_id):
    self._group_id = int(group_id)
    self._id = 'hueGroup-' + str(self._group_id)
    self._name = raw_data['name']
    self._lights = raw_data['lights']
    self._on = raw_data['action']['on']
    self._hue = raw_data['action']['hue']
    self._sat = raw_data['action']['sat']
    self._effect = raw_data['action']['effect']
    self._xy = raw_data['action']['xy']
    self._colormode = raw_data['action']['colormode']
    self._alert = raw_data['action']['alert']
    self._bri = raw_data['action']['bri']
    self._type = raw_data['type']
    self._bridge = bridgeID

    self._commands = {
      'on' : self.setOn,
      'off' : self.off,
      'switch' : self.switch,
      'update' : self.update
    }
    self._requests = {
      'on': self.getOn,
      'hue' : self.getHue,
      'bri' : self.getBri,
      'sat' : self.getSat
    }


  def sendEvent(self, event):
    logging.debug('Reciving Event in ' + str(metadata.get('module')) + ' ' + str(event))
    ''' NEED TO DECIDE WHAT TO DO HERE
    if event.deviceID == self._id:
      for item, value in event.event.iteritems():
        if item in self._commands: 
          self._commands[item](value)
    self.refreshData()
    '''

  def sendCommand(self, command):
    simpleCommand = None
    logging.debug('Reciving Command in ' + str(metadata.get('module')) + ' ' + str(command))
    if command.deviceID == self._id:
      for item, value in command.command.iteritems():
        if item in self._commands:
          simpleCommand = self._commands[item](value)
    
      ## OPTIONAL - SEND EVENT
      if command.simple:
        ffEvent(command.deviceID, simpleCommand)
      else:
        ffEvent(command.deviceID, command.command)
      ## OPTIONAL - SEND EVENT
      self.refreshData()

  def requestData(self, request):
    logging.debug('Request made to ' + str(metadata.get('module')) + ' ' + str(request) )
    if request.multi:
      returnData = {}
      for item in request.request:
        returnData[item] = self._requests[item]()
      return returnData

    elif not request.multi and not request.all:
      return self._requests[request.request]()

    elif request.all:
      returnData = self.refreshData()
      return returnData

  def refreshData(self):
    from core.firefly_api import update_status
    returnData = {}
    for item in self._requests:
      returnData[item] = self._requests[item]()
    returnData['deviceID'] = self._id
    update_status(returnData)
    return returnData

####################### START OF DEVICE CODE #############################

  @property
  def on(self):
      return self._on

  @on.setter
  def on(self, value):
    self._on = value
    self.set_light({'on':value})
    

  def off(self, args={}):
      self.set_light({'on':False})
      self._on = False
      return {'switch' : 'off'}

  @property
  def hue(self):
      return self._hue

  def switch(self, value):
    if value == 'on':
      self.on = True
    elif value == 'off':
      self.on = False

  def set_light(self, value):
    group_id = self._group_id
    lightEvent = ffCommand(self._bridge,{'sendGroupRequest' : {'groupID':group_id,'data':value}})
    


  def setOn(self, args={}):
    self.on = True
    return {'switch' : 'on'}



  def getOn(self):
    return self._on

  def getHue(self):
    return self._hue

  def getBri(self):
    return self._bri

  def getSat(self):
    return self._sat

  def update(self, raw_data):
    self._lights = raw_data['lights']
    self._on = raw_data['action']['on']
    self._hue = raw_data['action']['hue']
    self._sat = raw_data['action']['sat']
    self._effect = raw_data['action']['effect']
    self._xy = raw_data['action']['xy']
    self._colormode = raw_data['action']['colormode']
    self._alert = raw_data['action']['alert']
    self._bri = raw_data['action']['bri']
    self._type = raw_data['type']

    ffEvent(self._id, raw_data['action'])

