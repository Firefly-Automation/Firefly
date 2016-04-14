# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 18:06:51
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-11 20:50:14
import types

class Request(object):
  def __init__(self, deviceID, request, forceRefresh=False):
    self._deviceID = deviceID
    self._request = request
    self._forceRefresh = forceRefresh
    self._multi = isinstance(request, types.ListType)
    self._all = True if request == 'all' else False

  def __str__(self):
    return '<REQUEST DEVICE:' + str(self._deviceID) + ' REQUEST:' + str(self._request) + ' MULTI:' + str(self._multi) + ' ALL:' + str(self._all) + ' >'

  @property
  def deviceID(self):
      return self._deviceID
  
  @property
  def request(self):
      return self._request
  
  @property
  def forceRefresh(self):
      return self._forceRefresh

  @property
  def multi(self):
      return self._multi

  @property
  def all(self):
      return self._all
  
  
  