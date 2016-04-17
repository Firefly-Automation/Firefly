import logging
from core.models.event import Event as ffEvent

class Device(object):
  def __init__(self, deviceID, deviceName):
    self._id = deviceID
    self._name = deviceName
    self._type = self.METADATA.get('type')
    self._metadata = self.METADATA
    self._commands = self.COMMANDS
    self._requests = self.REQUESTS


  def __str__(self):
    status_string = '<DEVICE:' + self.type.upper() + ' ID:' + self.id.upper() + ' NAME:' + self.name.upper()
    for item in self.requests.keys():
      status_string += ' ' + item.upper() + ': ' + str(self.requests[item]()) 
    status_string += ' /DEVICE>'
    return status_string

  def sendEvent(self, event):
    logging.debug('Reciving Event in ' + str(self.metadata.get('module')) + ' ' + str(event))
    ''' NEED TO DECIDE WHAT TO DO HERE
    if event.deviceID == self._id:
      for item, value in event.event.iteritems():
      if item in self._commands: 
        self._commands[item](value)
    self.refreshData()
  '''

  def sendCommand(self, command):
    simpleCommand = None
    logging.debug('Reciving Command in ' + str(self.metadata.get('module')) + ' ' + str(command))
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
    logging.debug('Request made to ' + str(self.metadata.get('module')) + ' ' + str(request))
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

  @property
  def metadata(self):
      return self._metadata

  @property
  def name(self):
      return self._name

  @property
  def type(self):
      return self._type

  @property
  def id(self):
      return self._id
  
  
  
  