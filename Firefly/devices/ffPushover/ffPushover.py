# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 21:48:42
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-13 00:41:59
from core.models.event import Event as ffEvent
import logging

metadata = {
  'title' : 'Pushover Notifications',
  'author' : 'Zachary Priddy',
  'commands' : ['notify'],
  'capabilities' : ['notify'],
  'module' : 'ffPushover'
}

class Device(object):
  def __init__(self, deviceID, args={}):
    args = args.get('args')
    self._id = deviceID
    self._name = args.get('name')
    self._api_key = args.get('api_key')
    self._user_key = args.get('user_key')

    self._commands = {
      'notify' : self.notify
    }

    self._requests = {
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
    
      ## OPTIONAL - SEND EVENT
      if command.simple:
        ffEvent(command.deviceID, simpleCommand)
      else:
        ffEvent(command.deviceID, command.command)
      ## OPTIONAL - SEND EVENT
      #self.refreshData()

  def requestData(self, request):
    logging.debug('Request made to ffPushover ' + str(metadata.get('module')) + ' ' + str(request))
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

#############################################################33

  @property
  def api_key(self):
      return self._api_key

  @property
  def user_key(self):
      return self._user_key
  


  def notify(self, args):
    from core.firefly_api import http_request
    print "PUSHOVER NOTIFY"
    post_data = {
      'token':self.api_key,
      'user' : self.user_key,
      'title' : 'Firefly Notification',
      'message' : args.get('message'),
      'priority' : 0
    }

    if args.get('priority'):
      if args.get('priority') == 'low':
        post_data['priority'] = -1
      if args.get('priority') == 'high':
        post_data['priority'] = 1
      if args.get('priority') == 'emergency':
        post_data['priority'] = 2
        post_data['retry'] = '60'
        post_data['expire'] = '3600'

    if args.get('device'):
      post_data['device'] = args.get('device')

    http_request('https://api.pushover.net/1/messages.json',method='POST', data=post_data, callback=self.print_response_code)


  def print_response_code(self, response):
    logging.info('Pushover Response: ' + str(response))