# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 16:49:52
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-04-17 02:40:38

from core.models.event import Event as ffEvent
import logging

metadata = {
  'module' : 'ffPresence',
  'title' : 'Firefly Presence Device',
  'type' : 'device',
  'package' : 'ffPresence'
}

class Device(object):
  def __init__(self, deviceID, args={}):
    args = args.get('args')
    self._id = deviceID
    self._name = args.get('name')
    self._notify_present = args.get('notify_present')
    self.notify_not_present = args.get('notify_not_present')
    self.notify_device = args.get('notify_device')
    self._presence = True

    self._commands = {
      'presence' : self.setPresence
    }

    self._requests = {
      'presence' : self.getPresence
    }


  def __str__(self):
    return '<DEVICE:PRESENCE NAME:' + str(self._name) + ' ID:' + str(self._id) + ' PRESENCE:' + str(self._presence) + ' >'

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

      self.refreshData()

      ## OPTIONAL - SEND EVENT
      if command.simple:
        ffEvent(command.deviceID, simpleCommand)
      else:
        ffEvent(command.deviceID, command.command)
      ## OPTIONAL - SEND EVENT
      

  def requestData(self, request):
    logging.debug('Request made to ' + str(metadata.get('module')) + ' ' + str(request))
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


  def setPresence(self, value):
    from core.firefly_api import event_message
    if value is not self.presence:
      self.presence = value
      event_message(self._name, "Setting Presence To " + str(value))
      logging.debug("Setting Presence To " + str(value))
      

  def getPresence(self):
    return self.presence

  @property
  def presence(self):
      return self._presence

  @presence.setter
  def presence(self, value):
    self._presence = value
  