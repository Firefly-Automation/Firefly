# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-26 16:09:01
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-12 23:14:59

import logging

from core.models.app import App
from core.models.command import Command as ffCommand

class App(App):
  METADATA = {
      'title' : 'Firefly Advanced Lighting',
      'type' : 'app',
      'package' : 'ffAdvancedLighting',
      'module' : 'ffAdvancedLighting',
      'inputs' : {
        'motion_sensors' : {'type':'device', 'capability':'motion', 'multi':True, 'help':'Motion sensors to trigger lights', 'required':True},
        'lights' : {'capability':'switch', 'capability':'switch', 'multi':True, 'help':'Lights and Switches to be triggered by motion sensors', 'required':True}
      },
      'options' : {
        'delay_time' : {'type':'number', 'help':'Delay time in minutes from last activity before turnning off light', 'required':True},
        'run_modes' : {'type':'mode', 'multi':True, 'help':'Modes to run in.'},
        'no_run_modes' : {'type':'mode', 'multi':True, 'help':'Modes to not run in.'},
        'run_dark' : {'type':'boolean', 'help':'Run after senset'},
        'run_light' : {'type': 'boolean', 'help':'Run before sunset'}
      }
  }
  def __init__(self, config, args={}):
    configOptions = config # config.get('args')
    #METADAT is set above so that we can pull it during install
    #self.METADATA = METADATA

    self.INPUTS = {
      'motion_sensors' : configOptions.get('motion_sensors'),
      'lights' : configOptions.get('lights')
    }
    self.OPTIONS = {
      'delay_time' : configOptions.get('delay_time'),
      'run_modes' : configOptions.get('run_modes'),
      'no_run_modes' : configOptions.get('no_run_modes'),
      'run_dark' : configOptions.get('run_dark'),
      'run_light' : configOptions.get('run_light')
    }
    self.EVENTS = {
      'motion_sensors' : self.motionHandeler
    }
    self.COMMANDS = {
      'disable' : self.setDisable
    }

    self.REQUESTS = {
      'disable' : self.getDisable
    }
    super(App, self).__init__(config, args)

    self._disabled = False


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

  def motionHandeler(self, event={}):
    logging.critical('Motion Handeler!!!##')
    from core import ffScheduler
    from core import ffLocation

    logging.critical('Entered Motion Handeler')

    if self._disabled:
      logging.critical('Motion Events Disabled')
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
        retunr -2

    if self.run_light is not None:
      if not ffLocation.isLight:
        logging.critical("Not running because is light")
        return -2 

    if event.event.get('motion'):
      for light in self.lights:
        ffCommand(light,"on")
        ffScheduler.cancel(self._id)

    if not event.event.get('motion'):
      ffScheduler.runInM(self.delay_time, self.TurnLightsOff, replace=True, job_id=self._id)

  def TurnLightsOff(self):
    if self._disabled:
      logging.critical('Motion Events Disabled')
      return -2

    for light in self.lights:
      ffCommand(light, "off")




