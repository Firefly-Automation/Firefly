# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-18 20:56:52
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-12 23:16:14

import logging

from core import ffScheduler
from core.models.command import Command as ffCommand

class CTFade(object):
  def __init__(self, deviceID, startK, endK, fadeTimeS, startLevel, endLevel, run=True):
    self._deviceID = deviceID
    self._startK = startK
    self._endK = endK
    self._startLevel = startLevel
    self._endLevel = endLevel
    self._fadeTimeS = fadeTimeS

    self._timeRemaining = self._fadeTimeS
    self._currentK = self._startK
    self._currnetL = self._startLevel
    self._lStep = 0
    self._run = run

    self._interval = 0
    if self._fadeTimeS > 100:
      self._interval = 4
    if self._fadeTimeS > 300:
      self._interval = 10
    if self._fadeTimeS > 600:
      self._interval = 20
    if self._fadeTimeS > 900:
      self._interval = 30

    self._delay = int(self._fadeTimeS/self._interval) if self._fadeTimeS > 10 else 0 
    self._step = int(int(self._startK-self._endK)/self._interval) if self._fadeTimeS > 10 else 0
    if self._startLevel and self._endLevel:
      if abs(self._startLevel - self._endLevel) >= self._interval:
        self._lStep = int(int(self._endLevel-self._startLevel)/self._interval) if self._fadeTimeS > 10 else 0
      else:
        self._currnetL = self._endLevel

    #self._scheduler = Scheduler()

    if self._run:
      self.runFade()

  def runFade(self):
    if self._run:
      if self._startLevel and self._endLevel:
        lightCommand = ffCommand(self._deviceID, {'setLight':{'ct':str(self._currentK)+'K','transitiontime':self._delay*10,'level':self._currnetL, 'ctfade':True}})
        self._currnetL += self._lStep
      else:
        lightCommand = ffCommand(self._deviceID, {'setLight':{'ct':str(self._currentK)+'K','transitiontime':self._delay*10, 'ctfade':True}})
      if self._timeRemaining > 0:
        ffScheduler.runInS(int(self._delay), self.runFade, replace=True, job_id=self._deviceID)
      self._currentK -= self._step
      self._timeRemaining -= self._delay

  def endRun(self):
    logging.critical("Ending Fade")
    self._run = False




