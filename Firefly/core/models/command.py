# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 18:06:51
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-22 00:52:57
import types

class Command(object):
  def __init__(self, deviceID, command, routine=False, force=False, source=None):
    from core.firefly_api import send_command
    self._deviceID = deviceID
    self._command = command
    self._routine = routine
    self._force = force
    self._source = source
    self._simple = not isinstance(command, types.DictType) if command is not None else False
    if self._simple:
      self._command = {command:''}

    self._result = send_command(self)


  def __str__(self):
    return '<COMMAND DEVICE:' + str(self._deviceID) + ' COMMAND:' + str(self._command) + ' >'

  @property
  def log(self):
    return str({'device':self._deviceID,'command':self._command, 'source':self._source, 'routine':self._routine, 'force':self._force})

  @property
  def deviceID(self):
      return self._deviceID
  
  @property
  def command(self):
      return self._command
  
  @property
  def simple(self):
      return self._simple

  @property
  def routine(self):
      return self._routine

  @property
  def force(self):
      return self._force
  
  @property
  def result(self):
      return self._result

  @property
  def source(self):
      return self._source
  
  
  
  
  
