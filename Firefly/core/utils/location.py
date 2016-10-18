# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-09 23:39:47
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-17 22:09:32
import logging

from astral import Astral
from astral import GoogleGeocoder
from datetime import datetime
from datetime import timedelta

from core.utils.notify import Notification
from core.utils.scheduler import Scheduler

from core import ffEvent

DAY_EVENTS = ['dawn', 'sunrise', 'noon', 'sunset', 'dusk']

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
    for e in DAY_EVENTS:
      day_event_time = self.getNextDayEvent(e)
      logging.info('Day Event: {} Time: {}'.format(e, str(day_event_time)))
      self._scheduler.runAt(day_event_time, self.DayEventHandler, args=[e], job_id=e)

  def DayEventHandler(self, day_event):
    logging.info('day event handler - event: {}'.format(day_event))
    #TODO: Remove
    Notification('ZachPushover', 'LOCATION: is it {}'.format(day_event))
    ffEvent('location', {'time': day_event})
    next_day_event_time = self.getNextDayEvent(day_event)
    self._scheduler.runAt(next_day_event_time, self.DayEventHandler, args=[day_event], job_id=day_event)

  def getNextDayEvent(self, day_event):
    now = self.now
    day_event_time = self.city.sun(date=now, local=True).get(day_event)
    if day_event_time is None:
      return False
    if day_event_time < now:
      day_event_time = self.city.sun(date=now + timedelta(days=1), local=True).get(day_event)
    return day_event_time

  @property
  def mode(self):
    return self._mode

  @mode.setter
  def mode(self, mode):
    mode = str(mode)
    if mode in self.modes:
      self._mode = mode
      ffEvent('location', {'mode': self.mode})
      return True
    return False

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

  def isLightOffset(self, sunrise_offset=None):
    '''isLightOffset lets you know if the sun is up at the current time.

    If sunset_offset (INT Hours) is passed then it will tell you if the
    sun will be up in the next x hours from the current time.
    i.e: if you want to know if the sun will be up in the next three hours,
    you would pass sunrise_offset=-3

    [sunset_offset is yet to be added]
    '''
    if self.isDark:
      if sunrise_offset is not None:
        offset_time = self.now - timedelta(hours=sunrise_offset)
        sun = self._city.sun(date=self.now, local=True)
        if offset_time >= sun['sunrise'] or offset_time <= sun['sunset']:
          return True
        return False
    return not self.isDark

  @property
  def longitude(self):
    return self._longitude

  @property
  def latitude(self):
    return self._latitude

  @property
  def city(self):
    return self._city

  @property
  def now(self):
    return datetime.now(self._city.tz)
