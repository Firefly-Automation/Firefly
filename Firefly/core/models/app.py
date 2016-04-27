# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 09:54:21
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-26 21:10:05
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

import json
import logging
from collections import OrderedDict
from core.models.command import Command as ffCommand
from core.firefly_api import ffScheduler

class App(object):
  def __init__(self, config, args={}):
    #The config for each app will have its own json file - This way apps can easily be updated while running.
    #config = json.loads(configJson, object_pairs_hook=OrderedDict)
    self._id = config.get('id')
    self._name = config.get('name')
    self._metadata = self.METADATA
    self._commands = self.COMMANDS
    self._requests = self.REQUESTS
    self._options = self.OPTIONS
    self._inputs = self.INPUTS
    self._events = self.EVENTS
    self._listen = list(set().union(*(d for d in self._inputs.values())))

    for name, value in self._inputs.iteritems():
      setattr(self, name, value)

    for name, value in self._options.iteritems():
      setattr(self, name, value)

  def sendEvent(self, event):
    logging.critical('Reciving Event in ' + str(self._metadata.get('module')) + ' ' + str(event))

    logging.critical('Event from: ' + event.deviceID)
    for eventType in self._events:
      logging.critical(eventType)
      logging.critical(str(self._inputs))
      logging.critical(str(self._inputs.get(eventType)))
      if event.deviceID in self._inputs[eventType]:
        logging.critical(event.deviceID)
        self._events[eventType](event)

  def sendCommand(self, command):
    simpleCommand = None
    logging.debug('Reciving Command in ' + str(self._metadata.get('module')) + ' ' + str(command))
    if command.deviceID == self._id:
      for item, value in command.command.iteritems():
        if item in self._commands:
          simpleCommand = self._commands[item](value)

  @property
  def listen(self):
    return self._listen

  @property
  def id(self):
    return self._id
  