from Firefly import logging, scheduler
from Firefly.const import COMMAND_SET_LIGHT
from Firefly.helpers.events import Command

# TODO: Refactor this code.

class CTFade(object):
  def __init__(self, firefly, ff_id, start_k, end_k, fade_sec, start_level, end_level, run=True):
    self._firefly = firefly
    self._ff_id = ff_id
    self._startK = start_k
    self._endK = end_k
    self._startLevel = start_level
    self._endLevel = end_level
    self._fadeTimeS = fade_sec

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

    if self._run:
      self.runFade()

  def runFade(self):
    if self._run:
      if self._startLevel and self._endLevel:
        command = Command(self._ff_id, 'ct_fade', COMMAND_SET_LIGHT, ct=str(self._currentK)+'K', transitiontime=self._delay*10, level=self._currnetL, ct_fade=True)
        self._firefly.send_command(command)
        self._currnetL += self._lStep
      else:
        command = Command(self._ff_id, 'ct_fade', COMMAND_SET_LIGHT, ct=str(self._currentK) + 'K', transitiontime=self._delay * 10, ct_fade=True)
        self._firefly.send_command(command)

      if self._timeRemaining > 0:
        scheduler.runInS(int(self._delay), self.runFade, replace=True, job_id=self._ff_id+'_ct_fade')
      self._currentK -= self._step
      self._timeRemaining -= self._delay

  def endRun(self):
    logging.info("Ending Fade")
    self._run = False


