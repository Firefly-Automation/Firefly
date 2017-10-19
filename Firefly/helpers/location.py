import asyncio
from datetime import datetime, timedelta

from astral import Astral, GoogleGeocoder

from Firefly import logging, scheduler
from Firefly.const import DAY_EVENTS, EVENT_TYPE_BROADCAST, SOURCE_LOCATION, TIME
from Firefly.helpers.events import Event


class Location(object):
  def __init__(self, firefly, zipcode, modes, mode=None, last_mode=None, setup=True):
    logging.info('Setup Location')
    self._firefly = firefly
    self._modes = modes
    self._zipcode = zipcode
    self._isDark = True
    self._city = None

    # Status messages are information for the ui. Each is given an ID so that it can be removed later on.
    self.status_messages = {}

    if mode:
      self._mode = mode
    else:
      self._mode = self._modes[0]

    if last_mode:
      self._last_mode = last_mode
    else:
      self._last_mode = self.mode

    if setup:
      self._a = Astral(GoogleGeocoder)
      self._a.solar_depression = 'civil'
      self._city = self._a[self._zipcode]
      self._latitude = self._city.latitude
      self._longitude = self._city.longitude
      self.setupScheduler()

  def export(self, **kwargs) -> dict:
    export_data = {
      'modes':     self.modes,
      'mode':      self.mode,
      'last_mode': self.lastMode,
      'zipcode':   self._zipcode
    }
    return export_data

  # TODO: Add handling for realtime adding/deleting modes, changing zipcode etc.

  def setupScheduler(self) -> None:
    for e in DAY_EVENTS:
      day_event_time = self.getNextDayEvent(e)
      logging.info('Day Event: {} Time: {}'.format(e, str(day_event_time)))
      scheduler.runAt(day_event_time, self.DayEventHandler, day_event=e, job_id=e)

    event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, event_action={
      SOURCE_LOCATION: 'STARTUP'
    })
    self._firefly.send_event(event)

    # Setup Time Broadcast to start at the next minute
    now = self.now
    if now.second < 50:
      strat_at = now + timedelta(minutes=1) - timedelta(seconds=now.second)
    else:
      strat_at = now + timedelta(minutes=2) - timedelta(seconds=now.second)
    scheduler.runAt(strat_at, self.setup_time_broadcast)

  def setup_time_broadcast(self) -> None:
    # Setup Time Broadcast
    scheduler.runEveryM(1, self.broadcast_time)
    self.broadcast_time()

  @asyncio.coroutine
  def DayEventHandler(self, day_event):
    logging.info('day event handler - event: {}'.format(day_event))
    event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, event_action={
      SOURCE_LOCATION: day_event
    })
    self._firefly.send_event(event)
    next_day_event_time = self.getNextDayEvent(day_event)
    scheduler.runAt(next_day_event_time, self.DayEventHandler, day_event=day_event, job_id=day_event)

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
      self._last_mode = self._mode
      self._mode = mode
      event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, {
        'EVENT_ACTION_MODE': mode,
        'mode':              mode,
        'last_mode':         self.lastMode,
        'is_dark':           self.isDark
      })
      self.firefly.send_event(event)
      # Export location to file on change. This will be good for unexpected restarts.
      self.firefly.export_location()

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
        if offset_time >= sun['sunrise'] and offset_time <= sun['sunset']:
          return True
        return False
    return not self.isDark

  def broadcast_time(self) -> None:
    now = self.now
    event = Event(TIME, EVENT_TYPE_BROADCAST, {
      'epoch':   now.timestamp(),
      'day':     now.day,
      'month':   now.month,
      'year':    now.year,
      'hour':    now.hour,
      'minute':  now.minute,
      'weekday': now.isoweekday()
    })
    self.firefly.send_event(event)

  def add_status_message(self, message_id, message):
    self.status_messages[message_id] = message
    event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, event_action={
      'status_message': 'updated'
    })
    self._firefly.send_event(event)

  def remove_status_message(self, message_id):
    if message_id in self.status_messages:
      self.status_messages.pop(message_id)
      event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, event_action={
        'status_message': 'updated'
      })
      self._firefly.send_event(event)

  @property
  def longitude(self) -> int:
    return self._longitude

  @property
  def latitude(self) -> int:
    return self._latitude

  @property
  def city(self):
    return self._city

  @property
  def now(self) -> datetime:
    return datetime.now(self._city.tz)

  @property
  def firefly(self):
    return self._firefly
