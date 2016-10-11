# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 09:54:21
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-10 22:48:22
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
#from core.firefly_api import ffScheduler
from core import ffScheduler
from core.models.command import Command as ffCommand

class Routine(object):
  def __init__(self, configJson):
    config = json.loads(configJson, object_pairs_hook=OrderedDict)

    self._name = config.get('id')
    self._mode = config.get('mode')
    self._triggers = config.get('triggers')
    self._actions = config.get('actions')
    self._actions_day = config.get('actions_day')
    self._actions_night = config.get('actions_night')
    self._scheduling = config.get('scheduling')
    self._mode_no_run = config.get('mode_no_run')
    self._mode_run = config.get('mode_run')
    self._notification_devices = config.get('notification_devices')
    self._notification_message = config.get('notification_message')
    self._run_time_ranges = config.get('run_time_ranges')
    self._no_run_time_ranges = config.get('no_run_time_ranges')
    self._icon = config.get('icon')

    self._listen = list(set().union(*(d.keys() for d in self._triggers)))


    if self._scheduling:
      count = 0
      for cron_data in self._scheduling:
        uuid = self._name + str(count)
        #crondata = {'uuid':uuid, 'funct':self.executeRoutine, 'cron':cron_data}
        #ffScheduler.add_to_cron(crondata)
        ffScheduler.runSimpleWeekCron(self.executeRoutine, minute=cron_data.get('minute'), hour=cron_data.get('hour'), days_of_week=cron_data.get('days'), job_id=uuid)


  def __str__(self):
    return ('<ROUTINE>\nName: ' + str(self._name) + 
      '\nMode: ' + str(self._mode) + 
      '\nListen: ' + str(self._listen) + 
      '\n<END ROUTINE>')

  @property
  def listen(self):
      return self._listen

  @property
  def mode(self):
      return self._mode

  @property
  def triggers(self):
      return self._triggers

  @property
  def actions(self):
      return self._actions

  @property
  def scheduling(self):
      return self._scheduling


  def event(self, event):
    from core.firefly_api import send_request, event_message
    from core.models.request import Request as FFRequest
    from core.firefly_api import ffLocation
    logging.debug('ROUTINE: Receving Event In: ' + str(self._name))

    for trigger in self._triggers:
      if event.deviceID in trigger.keys():
        print 'Device in triggers'
        should_trigger = True
        for device, state in trigger.iteritems():
          #TEMP FIX
          if device != 'location':
            status = send_request(FFRequest(device,state.keys()[0]))
            if str(status) == str(state.values()[0]):
              pass
            else:
              should_trigger = False
          if device == 'location':
            if event.event == state:
              pass
            else:
              should_trigger = False

        if should_trigger:
          event_message(self._name,"Routine Triggered")
          print str(self._mode)
          self.executeRoutine()

  def executeRoutine(self, force=False):
    from time import sleep
    from datetime import datetime, time
    from core.firefly_api import ffLocation
    from core.utils.notify import Notification as ffNotification
    logging.debug("Executing Routine: " + self._name)

    if not force:
      if self._mode_no_run:
        if ffLocation.mode in self._mode_no_run:
          logging.debug('Returning: Set to not execute in mode: ' + ffLocation.mode)
          return

      if self._mode_run:
        if ffLocation.mode not in self._mode_run:
          logging.debug('Returning: Set to not execute in mode: ' + ffLocation.mode)
          return

      if self._run_time_ranges or self._no_run_time_ranges:
        now = datetime.now().time()
        if self._run_time_ranges:
          for timeRange in self._run_time_ranges:
            startH, startM = timeRange.get('start_time').split(':')
            startH = int(startH)
            startM = int(startM)
            endH, endM = timeRange.get('end_time').split(':')
            endH = int(endH)
            endM = int(endM)
            if startH <= endH:
              if not (now >= time(startH,startM) and now <= time(endH,endM)):
                logging.critical("Not in time range to run routine")
                return
            else:
              if not (now >= time(startH,startM) or now <= time(endH,endM)):
                logging.critical("Not in time range to run routine")
                return

        if self._no_run_time_ranges:
          for timeRange in self._no_run_time_ranges:
            startH, startM = timeRange.get('start_time').split(':')
            startH = int(startH)
            startM = int(startM)
            endH, endM = timeRange.get('end_time').split(':')
            endH = int(endH)
            endM = int(endM)
            logging.critical(str(startH) + ' ' + str(endH))
            if startH <= endH:
              if now >= time(startH,startM) and now <= time(endH,endM):
                logging.critical("In time range to not run routine")
                return
            else:
              if now >= time(startH,startM) or now <= time(endH,endM):
                logging.critical("In time range to not run routine")
                return



    for device, commands in self._actions.iteritems():
      ffCommand(device,commands)
      if 'hue' in device:
        sleep(0.5)

    if ffLocation:
      if ffLocation.isLight:
        for device, commands in self._actions_day.iteritems():
          ffCommand(device,commands)
          if 'hue' in device:
            sleep(0.5)

      if ffLocation.isDark:
        for device, commands in self._actions_night.iteritems():
          ffCommand(device,commands)
          if 'hue' in device:
            sleep(0.5)

    if self._mode:
      ffLocation.mode = self._mode

    if self._notification_devices and self._notification_message:
      for device in self._notification_devices:
        ffNotification(device, self._notification_message)




  


  
  
  
  
