# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 09:24:49
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-11 09:26:34

class Settings(object):

  def __init__(self):
    self._ip_address = None
    self._port = None

  def __str__(self):
    return 'IP Address: ' + str(self._ip_address) + ' Port: ' + str(self._port)

  @property
  def port(self):
      return self._port

  @port.setter
  def port(self, value):
    self._port = value

  @property
  def ip_address(self):
      return self._ip_address

  @ip_address.setter
  def ip_address(self, value):
    self._ip_address = value
