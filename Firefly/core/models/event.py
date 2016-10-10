# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 16:18:14
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-09 23:25:39



class Event(object):
  def __init__(self,deviceID,eventDict,sendToDevice=True,eventFrom=None):
    from core import sendEvent

    self._deviceID = deviceID
    self._event = eventDict
    self._sendToDevice = sendToDevice
    self._eventFrom = eventFrom
    self._result = sendEvent(self)

  def __str__(self):
    return '<EVENT DEVICE: ' + str(self._deviceID) + ' EVENT: ' + str(self._event) + ' >'

  @property
  def log(self):
    return str({'Device':self._deviceID,'Event':self._event,'From':self._eventFrom,'Send To Device':self._sendToDevice})

  @property
  def deviceID(self):
      return self._deviceID

  @property
  def event(self):
      return self._event

  @property
  def result(self):
      return self._result

  @property
  def sendToDevice(self):
      return self._sendToDevice

  @property
  def eventFrom(self):
      return self._eventFrom
  
  
  
  
  