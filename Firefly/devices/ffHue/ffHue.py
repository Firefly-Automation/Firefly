# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 21:48:42
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-12 23:07:46
from core.models import event
from core.models.command import Command as ffCommand

#from core.scheduler import Scheduler
import ffHue_bridge as bridge
import ffHue_group as groupDevice
import ffHue_light as lightDevice
import logging

from core import ffScheduler

metadata = {
  'title' : 'Pushover Notifications',
  'author' : 'Zachary Priddy',
  'commands' : ['notify'],
  'capabilities' : ['notify'],
}

class Device(object):
  def __init__(self, deviceID, args={}):
    args = args.get('args')
    self._id = deviceID
    self._name = args.get('name')
    self._install_lights = args.get('install_lights')
    self._install_groups = args.get('install_groups')
    self._username = args.get('username')
    self._hueBridge = None

    self._commands = {
      'startup' : self.refresh_scheduler
    }

    self._requests = {
    }

    self.VIEWS = {}

    self.install_hue()


  def sendEvent(self, event):
    logging.debug('Reciving Event in ffHue ' + str(event) )
    if event.deviceID == self._id:
      for item, value in event.event.iteritems():
        if item in self._commands: 
          self._commands[item](value)
    self.refreshData()

  def requestData(self, request):
    logging.debug('Request made to ffHue ' + str(request))
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

  def install_hue(self):
    from core.firefly_api import install_child_device
    logging.debug("Installing Hue Bridge")
    self._hueBridge = bridge.Bridge(deviceID='ffHueBridge', username=self._username)
    install_child_device('ffHueBridge',self._hueBridge)

    rawLightData = self._hueBridge.get_lights()
    for light, lightData in rawLightData.iteritems():
      lightData['bridgeID'] = 'ffHueBridge'
      lightConfig = {}
      lightConfig['args'] = lightData
      lightConfig['args']['lightID'] = light
      newLight = lightDevice.Device('hue-light-' + str(light), lightConfig)
      lightData['args'] = {}
      lightData['args']['name'] = lightData.get('name')
      install_child_device('hue-light-' + str(light), newLight, config=lightData)

    rawGroupData = self._hueBridge.get_groups()
    for group, groupData in rawGroupData.iteritems():
      groupData['bridgeID'] = 'ffHueBridge'
      groupConfig = {}
      groupConfig['args'] = groupData
      groupConfig['args']['groupID'] = group
      newGroup = groupDevice.Device('hue-group-' + str(group), groupConfig)
      groupData['args'] = {}
      groupData['args']['name'] = groupData.get('name')
      install_child_device('hue-group-' + str(group), newGroup, config=groupData)

    self.refresh_scheduler()

  def refresh_scheduler(self, args={}):
    logging.debug("Starting Hue Scheduler")
    #hueScheduler = Scheduler()
    ffScheduler.runEveryS(10,self.refresh_hue,replace=True,job_id='HueRefresher')

  def refresh_hue(self):
    rawLightData = self._hueBridge.get_lights()
    for light, lightData in rawLightData.iteritems():
      deviceID = 'hue-light-' + str(light)
      updateEvent =ffCommand(deviceID,{'update':lightData})

    rawGroupData = self._hueBridge.get_groups()
    for group, groupData in rawGroupData.iteritems():
      deviceID = 'hue-group-' + str(group)
      updateEvent = ffCommand(deviceID,{'update':groupData})