# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 18:06:51
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-04-19 00:39:02
import types

class Command(object):
  def __init__(self, deviceID, command, routine=False):
    from core.firefly_api import send_command
    self._deviceID = deviceID
    self._command = command
    self._routine = routine
    self._simple = not isinstance(command, types.DictType)
    if self._simple:
      self._command = {command:''}

    send_command(self)


  def __str__(self):
    return '<COMMAND DEVICE:' + str(self._deviceID) + ' COMMAND:' + str(self._command) + ' >'

  @property
  def log(self):
    return str({'Device':self._deviceID,'Command':self._command})

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
  
  
  
  