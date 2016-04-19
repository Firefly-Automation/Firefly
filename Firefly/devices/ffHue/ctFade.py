# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-18 20:56:52
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-04-18 23:55:37

from core.scheduler import Scheduler
from core.models.command import Command as ffCommand

class CTFade(object):
  def __init__(self, deviceID, startK, endK, fadeTimeS, run=True):
    self._deviceID = deviceID
    self._startK = startK
    self._endK = endK
    self._fadeTimeS = fadeTimeS

    self._timeRemaining = self._fadeTimeS
    self._currentK = self._startK
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

    self._scheduler = Scheduler()

    if self._run:
      self.runFade()

  def runFade(self):
    if self._run:
      lightCommand = ffCommand(self._deviceID, {'setLight':{'ct':str(self._currentK)+'K','transitiontime':self._delay*10,'ctfade':True}})
      if self._timeRemaining >= self._delay:
        self._scheduler.runInS(int(self._delay), self.runFade, replace=True, uuid=self._deviceID)
      self._currentK -= self._step
      self._timeRemaining -= self._delay

  def endRun(self):
    self._run = False




