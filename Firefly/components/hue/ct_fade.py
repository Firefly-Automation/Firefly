from Firefly import logging, scheduler
from Firefly.const import COMMAND_SET_LIGHT
from Firefly.helpers.events import Command


# TODO: Refactor this code.

class CTFade(object):
  def __init__(self, firefly, ff_id, start_k, end_k, fade_sec, start_level=100, end_level=100, run=True):
    if type(start_level) is not int:
      start_level = 100
    if type(end_level) is not int:
      end_level = 100

    self._firefly = firefly
    self._ff_id = ff_id
    self._start_ct = start_k
    self._end_ct = end_k
    self._start_level = max(start_level, 1)
    self._end_level = end_level
    self._fade_sec = fade_sec
    self._run = run

    self._time_remaining = self._fade_sec
    self._current_ct = self._start_ct
    self._current_level = self._start_level
    self._level_step = 0
    self._first_run = True

    self._interval = 1
    if self._fade_sec > 100:
      self._interval = 4
    if self._fade_sec > 300:
      self._interval = 10
    if self._fade_sec > 600:
      self._interval = 20
    if self._fade_sec > 900:
      self._interval = 30

    self._delay = calculate_delay(self._interval, self._fade_sec)
    self._ct_step = calculate_ct_step(self._interval, self._fade_sec, self._start_ct, self._end_ct)

    self._level_control = True if self._start_level and self._end_level else False
    if self._level_control:
      self._level_step = calculate_level_step(self._interval, self._fade_sec, self._start_level, self._end_level)
      if self._level_step == 0:
        self._current_level = self._end_level

    if self._run:
      self.runFade()

  def runFade(self):
    if not self._run:
      return

    if self._first_run:
      if self._level_control:
        command = Command(self._ff_id, 'ct_fade', COMMAND_SET_LIGHT, level=self._current_level,
                          ct=ct_string(self._start_ct), ct_fade=True, transitiontime=1)
      else:
        command = Command(self._ff_id, 'ct_fade', COMMAND_SET_LIGHT, ct=ct_string(self._start_ct), ct_fade=True,
                          transitiontime=1)
      self._firefly.send_command(command)
      self._first_run = False

    self._current_ct += self._ct_step
    self._time_remaining -= self._delay
    if self._level_control:
      self._current_level += self._level_step

    if self._level_control:
      command = Command(self._ff_id, 'ct_fade', COMMAND_SET_LIGHT, ct=ct_string(self._current_ct),
                        transitiontime=self._delay * 10, level=self._current_level, ct_fade=True)
    else:
      command = Command(self._ff_id, 'ct_fade', COMMAND_SET_LIGHT, ct=ct_string(self._current_ct),
                        transitiontime=self._delay * 10, ct_fade=True)

    self._firefly.send_command(command)

    if self._time_remaining > 0:
      scheduler.runInS(int(self._delay), self.runFade, replace=True, job_id=self._ff_id + '_ct_fade')
    else:
      self.send_last_fade()

  def send_last_fade(self):
    if self._level_control:
      command = Command(self._ff_id, 'ct_fade', COMMAND_SET_LIGHT, ct=ct_string(self._end_ct),
                        transitiontime=self._delay * 10, level=self._end_level, ct_fade=True)
    else:
      command = Command(self._ff_id, 'ct_fade', COMMAND_SET_LIGHT, ct=ct_string(self._end_ct),
                        transitiontime=self._delay * 10, ct_fade=True)

    self._firefly.send_command(command)
    self.endRun()



  def endRun(self):
    logging.info("Ending Fade")
    self._run = False
    self._first_run = True


def calculate_delay(interval: int, fade_sec: int):
  if fade_sec < 10:
    return 0
  return int(fade_sec / interval)


def calculate_ct_step(interval: int, fade_sec: int, start_ct: int, end_ct: int):
  if fade_sec < 10:
    return end_ct
  else:
    return int((end_ct - start_ct) / interval)


def calculate_level_step(interval: int, fade_sec: int, start_level: int, end_level: int):
  if abs(start_level - end_level) <= interval or fade_sec < 10:
    return start_level
  return int((end_level - start_level) / interval)


def ct_string(ct):
  return '%sK' % ct
