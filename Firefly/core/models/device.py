import logging

from core.models.event import Event as ffEvent


class Device(object):
  def __init__(self, deviceID, deviceName):
    self._id = deviceID
    self._name = deviceName
    self._type = self.METADATA.get('type')
    self._lastStatus = {}
    self._metadata = self.METADATA
    self._commands = self.COMMANDS
    self._requests = self.REQUESTS
    self._views = self.VIEWS

    self.refreshData()


  def __str__(self):
    status_string = '<DEVICE:' + self.type.upper() + ' ID:' + self.id.upper() + ' NAME:' + self.name.upper()

    for item in self.requests.keys():
      status_string += ' ' + item.upper() + ': ' + str(self.requests[item]()) 
    status_string += ' /DEVICE>'
    return status_string

  def sendEvent(self, event):
    logging.debug('Reciving Event in ' + str(self.metadata.get('module')) + ' ' + str(event))
    if event.event.get('startup'):
      self.refreshData()
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

      updated_status = self.refreshData()
      if command.send_event:
        if updated_status:
          ffEvent(self.id, updated_status)
        else:
          logging.debug('NO chnage in status')
      else:
        logging.debug('Set to not send event')
    

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
    logging.debug('Refresh Data in ' + self._name)
    from core.firefly_api import update_status
    returnData = {}
    '''
    allData = dict(self.__dict__)
    if allData.get('COMMANDS'):
      allData.pop('COMMANDS', None)
    if allData.get('REQUESTS'):
      allData.pop('REQUESTS',None)
    if allData.get('_commands'):
      allData.pop('_commands', None)
    if allData.get('_requests'):
      allData.pop('_requests', None)
    logging.critical(allData)
    returnData = allData
    '''
    newChanges = {}
    for item in self._requests:
      returnData[item] = self._requests[item]()
      #This builds a list of only the things that have changed - This way an event can be sent with only those items
      if returnData[item] != self._lastStatus.get(item):
        newChanges[item] = returnData[item]
    self._lastStatus = returnData
    returnData['deviceID'] = self._id
    returnData['views'] = self._views
    updated = update_status(returnData)
    if updated and newChanges != {}:
      return newChanges

    return False

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

  @property
  def requests(self):
      return self._requests

  @property
  def views(self):
    return self._views