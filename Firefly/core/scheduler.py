#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @FileName: scheduler.py
# @Author: Zachary Priddy
# @Date:   2016-02-13 21:34:27
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-03-04 22:48:44
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from twisted.internet import reactor, task
from uuid import uuid1
from crontab import CronTab

'''Sample cron_data = {'uuid':'blah','funct':s,'cron':'0 8 * * 1'}  **UUID is optional'''
'''Or crondata can be  cron_data = {'uuid':'blah','funct':s,'cron':'0 8 * * MON,TUE'}'''

class Scheduler(object):
  def __init__(self):
    self._queue = {}
    self._loop = {}
    self._cron = {}

  def add_to_queue(self, item, replace=False, uuid=None):
    if replace and not uuid:
      return False
    if replace and self._queue.get(uuid):
      if self._queue[uuid].active():
        self._queue[uuid].cancel()
    if not uuid:
      uuid = uuid1()
    self._queue[uuid] = item

    return uuid

  def add_to_loop(self, delay, function, replace=False, uuid=None):
    print "ADD TO LOOP"
    if replace and not uuid:
      return False
    if replace and self._loop.get(uuid):
      try:
        self._loop[uuid].stop()
      except:
        pass
    if not uuid:
      uuid = uuid1()
    self._loop[uuid] = task.LoopingCall(function)
    self._loop[uuid].start(delay)

    return uuid

  def cancel(self, uuid):
    if self._queue.get(uuid):
      if self._queue[uuid].active():
        self._queue[uuid].cancel()
      return True
    if self._loop.get(uuid):
      self._loop[uuid].stop()
      return True
    return False

  def add_to_cron(self, cron_data, uuid=None):
    print 'Adding to cron'
    if not cron_data.get('uuid') and not uuid:
      return False
    if not cron_data.get('uuid'):
      cron_data['uuid'] = uuid1()
    uuid = cron_data['uuid']
    delay = CronTab(cron_data['cron']).next()
    self._cron[uuid] = reactor.callLater(delay, self.runCron, cron_data)
    return uuid

  def runCron(self, cron_data):
    '''Only run if uuid is in cron dict'''
    if self._cron.get(cron_data['uuid']):
      function = cron_data['funct']
      cron = cron_data['cron']
      function()
      self.add_to_cron(cron_data)

  def del_cron(self, uuid):
    '''Removing uuid from cron dict will prevent it from running again'''
    if self._cron.get(cron_data['uuid']):
      del self._cron['uuid']


  def runInS(self, delay, function, replace=False, uuid=None):
    return self.add_to_queue(reactor.callLater(delay, function), replace, uuid)

  def runInM(self, delay, function, replace=False, uuid=None):
    return self.add_to_queue(reactor.callLater(delay*60, function), replace, uuid)

  def runInH(self, delay, function, replace=False, uuid=None):
    return self.add_to_queue(reactor.callLater(delay*60*60, function), replace, uuid)

  def runEveryS(self, delay, function, replace=False, uuid=None):
    return self.add_to_loop(delay, function, replace, uuid)

  def runEveryM(self, delay, function, replace=False, uuid=None):
    return self.add_to_loop(delay*60, function, replace, uuid)

  def runEveryH(self, delay, function, replace=False, uuid=None):
    return self.add_to_loop(delay*60*60, function, replace, uuid)
