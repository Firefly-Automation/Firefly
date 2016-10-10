# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-09 23:39:47
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-09 23:53:51
from astral import Astral
from astral import GoogleGeocoder
from datetime import datetime, timedelta

from core.utils.scheduler import Scheduler

from core import ffEvent

class Location(object):
  def __init__(self, zipcode, modes):
    self._modes=modes
    self._zipcode = zipcode
    self._isDark = True
    self._city = None

    self._a = Astral(GoogleGeocoder)
    self._a.solar_depression = 'civil'
    self._city = self._a[self._zipcode]
    self._latitude = self._city.latitude
    self._longitude = self._city.longitude

    self._mode = self._modes[0]
    self._last_mode = self.mode

    self._scheduler = Scheduler()

    self.setupScheduler()



  def setupScheduler(self):
    now = self.now

    # TODO: Make a more global function
    dawn_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['dawn']
    if dawn_time < now:
      dawn_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dawn']
    logging.debug("Dawn Time: " + str(dawn_time))
    delay_s = (dawn_time - now).total_seconds()
    self._scheduler.runInS(delay_s, self.dawn_handler, replace=True, job_id='DawnScheduler')


  @mode.setter
  def mode(self, mode):
    mode = str(mode)
    if mode in self.modes:
      self._mode = mode
      ffEvent('location':{'mode':self.mode})
      return True
    return False

  @property
  def mode(self):
    return self._mode

  @property
  def modes(self):
    return self._modes

  @property
  def lastMode(self):
    return self._last_mode

  @property
  def isDark(self):
    now = self.now
    sun = self._city.sun(date=now, local=True)
    if now >= sun['sunset'] or now <= sun['sunrise']:
      return True
    return False

  @property
  def isLight(self):
    return not self.isDark

  @property
  def longitude(self):
    return self._longitude

  @property
  def latitude(self):
    return self._latitude

  @property
  def now(self):
    return datetime.now(self._city.tz) 
