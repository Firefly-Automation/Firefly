# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-19 15:57:29
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-09 23:27:57
import json
import logging

from astral import Astral
from astral import GoogleGeocoder
from datetime import datetime, timedelta

from core.models.command import Command as ffCommand
from core.models.event import Event as ffEvent
from core.scheduler import Scheduler as ffScheduler
from core.utils.notify import Notification as ffNotify

from core.utils.scheduler import Scheduler

l_scheduler = ffScheduler()

location_scheduler = Scheduler()


class Location(object):
  def __init__(self, config_file):
    self._config_file = config_file
    self._modes = []
    self._a = None
    self._city = None
    self._zipcode = None
    self._isDark = True
    self._weather = None

    self._latitude = None
    self._longitude = None
    self.read_config_file()
    self.setup_local()

    self._mode = self._modes[0]
    self._last_mode = self._modes[0]
    
  @property
  def mode(self):
    return self._mode

  @property
  def last_mode(self):
    return self._last_mode

  @property
  def isDark(self):
    now = self.now()
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
  
  
  
  @mode.setter
  def mode(self, value):
    value = str(value)
    if value in self._modes:
      self._last_mode = self._mode
      self._mode = value
      ffEvent('location',{'mode':self._mode})
      return True
    return False

  def read_config_file(self):
    with open(self._config_file) as data_file:
      config = json.load(data_file)
      self._zipcode = config.get('zip_code')
      self._modes = config.get('modes')

      logging.debug("Modes Installed: " + str(self._modes))
      logging.debug("Zipcode: " + str(self._zipcode))

  def setup_local(self):
    self._a = Astral(GoogleGeocoder)
    self._a.solar_depression = 'civil'
    self._city = self._a[self._zipcode]
    self._latitude = self._city.latitude
    self._longitude = self._city.longitude

    #Prep Timers 
    dawn_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['dawn']
    now = self.now()
    if dawn_time < now:
      dawn_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dawn']
    logging.debug("Dawn Time: " + str(dawn_time))
    delay_s = (dawn_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.dawn_handler, replace=True, uuid='DawnScheduler')
    location_scheduler.runInS(delay_s, self.dawn_handler, replace=True, job_id='DawnScheduler')

    sunrise_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['sunrise']
    now = self.now()
    if sunrise_time < now:
      sunrise_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['sunrise']
    logging.debug("Sunrise Time: " + str(sunrise_time))
    delay_s = (sunrise_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.sunrise_handler, replace=True, uuid='SunriseScheduler')

    noon_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['noon']
    now = self.now()
    if noon_time < now:
      noon_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['noon']
    logging.debug("Noon Time: " + str(noon_time))
    delay_s = (noon_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.noon_handler, replace=True, uuid='NoonScheduler')

    sunset_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['sunset']
    now = self.now()
    if sunset_time < now:
      sunset_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['sunset']
    logging.debug("Sunset Time: " + str(sunset_time))
    delay_s = (sunset_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.sunset_handler, replace=True, uuid='SunsetScheduler')

    dusk_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['dusk']
    now = self.now()
    if dusk_time < now:
      dusk_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dusk']
    logging.debug("Dusk Time: " + str(dusk_time))
    delay_s = (dusk_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.dusk_handler, replace=True, uuid='DuskScheduler')



  def dawn_handler(self):
    ffNotify('ZachPushover', 'LOCATION: It is dawn!')
    ffEvent('location',{'time':'dawn'})
    now = self.now()
    dawn_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dawn']
    logging.debug("Dawn Time: " + str(dawn_time))
    delay_s = (dawn_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.dawn_handler, replace=True, uuid='DawnScheduler')

  def sunrise_handler(self):
    ffNotify('ZachPushover', 'LOCATION: It is sunrise!')
    ffEvent('location',{'time':'sunrise'})
    now = self.now()
    sunrise_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['sunrise']
    logging.debug("Sunrise Time: " + str(sunrise_time))
    delay_s = (sunrise_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.sunrise_handler, replace=True, uuid='SunriseScheduler')

  def noon_handler(self):
    ffNotify('ZachPushover', 'LOCATION: It is noon!')
    ffEvent('location',{'time':'noon'})
    now = self.now()
    noon_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['noon']
    logging.debug("Noon Time: " + str(noon_time))
    delay_s = (noon_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.noon_handler, replace=True, uuid='NoonScheduler')

  def sunset_handler(self):
    ffNotify('ZachPushover', 'LOCATION: It is sunset!')
    ffEvent('location',{'time':'sunset'})
    now = self.now()
    sunset_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['sunset']
    logging.debug("Sunset Time: " + str(sunset_time))
    delay_s = (sunset_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.sunset_handler, replace=True, uuid='SunsetScheduler')

  def dusk_handler(self):
    ffNotify('ZachPushover', 'LOCATION: It is dusk!')
    ffEvent('location',{'time':'dusk'})
    now = self.now()
    dusk_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dusk']
    logging.debug("Dusk Time: " + str(dusk_time))
    delay_s = (dusk_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.dusk_handler, replace=True, uuid='DuskScheduler')

  def now(self):
    return datetime.now(self._city.tz)
