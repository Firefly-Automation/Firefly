# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-26 23:06:59
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-10 22:52:38


import logging

from core.models.app import App
from core.models.command import Command as ffCommand

class App(App):
  METADATA = {
      'title' : 'Firefly Advanced Lighting - Motion',
      'type' : 'app',
      'package' : 'ffAdvancedLighting',
      'module' : 'switch',
      'inputs' : {
        'switches' : {'type':'device', 'capability':'switch', 'multi':True, 'help':'Switches to trigger lights', 'required':True},
        'lights' : {'type':'device', 'capability':'switch', 'multi':True, 'help':'Lights and Switches to be triggered by switches', 'required':True},
        'actions_switch_on' : {'type':'action', 'multi':True, 'help':'Non generic actions when switch turns on'},
        'actions_switch_off' : {'type':'action', 'multi':True, 'help':'Non generic actions when switch turns off'}
      },
      'options' : {
        'delay_time' : {'type':'number', 'help':'Delay time in minutes from last activity before off actions applied', 'required':True},
        'run_modes' : {'type':'mode', 'multi':True, 'help':'Modes to run in.'},
        'no_run_modes' : {'type':'mode', 'multi':True, 'help':'Modes to not run in.'},
        'run_dark' : {'type':'boolean', 'help':'Run after senset'},
        'run_light' : {'type': 'boolean', 'help':'Run before sunset'},
        'run_conditions' : {'type':'device-states', 'multi':True, 'help':'Run only if devices in these states'},
        'no_run_conditions' : {'type':'device-states', 'multi':True, 'help':'Dont run if devices in these states'},
        'allow_chain' : {'type':'boolean', 'default':False, 'help':'Allow the actions of this event to trigger other events listening to switched devices. This is not recommened because it can cause looping.'}
      }
  }

  def __init__(self, config, args={}):
    #METADAT is set above so that we can pull it during install
    #self.METADATA = METADATA
    self.INPUTS = {
      'switches' : config.get('switches'),
      'lights' : config.get('lights'),
      'actions_switch_on' : config.get('actions_switch_on'),
      'actions_switch_off' : config.get('actions_switch_off')
    }
    self.OPTIONS = {
      'delay_time' : config.get('delay_time'),
      'run_modes' : config.get('run_modes'),
      'no_run_modes' : config.get('no_run_modes'),
      'run_dark' : config.get('run_dark'),
      'run_light' : config.get('run_light'),
      'run_conditions' : config.get('run_conditions'),
      'no_run_conditions' : config.get('no_run_modes')
    }
    self.EVENTS = {
      'switches' : self.switchHandler
    }
    self.COMMANDS = {
      'disable' : self.setDisable
    }

    self.REQUESTS = {
      'disable' : self.getDisable
    }
    super(App, self).__init__(config, args)

    self._disabled = False
    self._send_event = True if config.get('allow_chain') is True else False


  #########################################
  # END OF SETUP
  #########################################

  def setDisable(self, value):
    logging.critical('Setting Disabled to ' + str(value))
    if self._disabled:
      self._disabled = False
    else:
      self._disabled = True

  def getDisable(self, args={}):
    return self._disabled

  def switchHandler(self, event={}):
    from core.firefly_api import ffScheduler
    from core.firefly_api import ffLocation

    if self._disabled:
      logging.critical('Switch Events Disabled')
      return -2

    if self.run_modes:
      if ffLocation.mode not in self.run_modes:
        logging.critical("Not in mode to run")
        return -2

    if self.no_run_modes:
      if ffLocation.mode in self.no_run_modes:
        logging.critical("In no run mode")
        return -2

    if self.run_dark is not None:
      if not ffLocation.isDark:
        logging.critical("Not running because is dark")
        return -2

    if self.run_light is not None:
      if not ffLocation.isLight:
        logging.critical("Not running because is light")
        return -2 

    if event.event.get('on'):
      if self.lights:
        for light in self.lights:
          ffCommand(light,"on", send_event=self._send_event)
      if self.actions_switch_on:
        for device, action in self.actions_switch_on.iteritems():
          ffCommand(device, action, send_event=self._send_event)
      ffScheduler.cancel(self._id)

    if not event.event.get('on'):
      if self.delay_time is None:
        self.TurnLightsOff()
      else:
        ffScheduler.runInM(self.delay_time, self.TurnLightsOff, replace=True, job_id=self._id)

  def TurnLightsOff(self):
    from core.firefly_api import ffScheduler
    from core.firefly_api import ffLocation
    
    if self._disabled:
      logging.critical('Switch Events Disabled')
      return -2

    if self.run_modes:
      if ffLocation.mode not in self.run_modes:
        logging.critical("Not in mode to run")
        return -2

    if self.no_run_modes:
      if ffLocation.mode in self.no_run_modes:
        logging.critical("In no run mode")
        return -2

    if self.lights:
      for light in self.lights:
        ffCommand(light, "off", send_event=self._send_event)

    if self.actions_switch_off:
      for device, action in self.actions_switch_off.iteritems():
        ffCommand(device, action, send_event=self._send_event)
        if 'hue' in device:
          sleep(0.5)


