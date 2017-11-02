import asyncio
import pickle
from datetime import datetime, timedelta
import json
from os import path

from astral import Astral, GoogleGeocoder

from Firefly import logging, scheduler
from Firefly.const import DAY_EVENTS, EVENT_TYPE_BROADCAST, SOURCE_LOCATION, TIME, LOCATION_FILE
from Firefly.helpers.events import Event, Command


class Location(object):
  def __init__(self, firefly, location_file=LOCATION_FILE):
    logging.info('Setup Location')
    self.firefly = firefly
    self.modes = ['home']
    self._mode = 'home'
    self.geolocation = None
    self.address = 'San Fransisco'
    self.old_address = None
    self.location_dump = None

    self.read_config(location_file)
    if self.old_address == self.address and self.geolocation:
      logging.info('Importing location from pickle file')
    else:
     self.update_location(self.address)

    self.status_messages = {}

    self.setupScheduler()


  def read_config(self, location_file, **kwargs):
    ''' Read config from file

    Args:
      location_file: path to location config file
      **kwargs:

    Returns:

    '''
    with open(location_file) as config_file:
      config = json.load(config_file)
      self.location_file = location_file
      self.modes = config.get('modes', ['home'])
      self._mode = config.get('mode', 'home')
      self._last_mode = config.get('last_mode', 'home')
      self.address = config.get('address', 'San Fransisco')
      self.old_address = config.get('old_address', '')

    pickle_file = location_file.replace('.json', '.pickle')
    if path.isfile(pickle_file):
      self.geolocation = pickle.load(open(pickle_file, 'rb'))


  def update_location(self, address:str, **kwargs):
    ''' Update location to new address

    Args:
      address: New address for location
      **kwargs:

    Returns:

    '''
    a = Astral(GoogleGeocoder)
    a.solar_depression = 'civil'
    self.geolocation = a[address]
    address = '%s %s' % (self.geolocation.name, self.geolocation.region)
    self.old_address = address
    self.address = address
    self.export_to_file()
    self.setupScheduler()


  @property
  def latitude(self):
    return self.geolocation.latitude

  @property
  def longitude(self):
    return self.geolocation.longitude

  def add_mode(self, mode, **kwargs):
    mode = mode.lower()
    if mode not in self.modes:
      self.modes.append(mode)

  def remove_mode(self, mode, **kwargs):
    mode = mode.lower()
    if mode in self.modes:
      self.modes.remove(mode)

  def export_to_file(self, **kwargs):
    ''' Save the config to the config file

    Args:
      **kwargs:

    Returns:

    '''
    with open(self.location_file, 'w') as config:
      json.dump(self.export(), config, indent=4, sort_keys=True)

    pickle_file = self.location_file.replace('.json', '.pickle')
    with open(pickle_file, 'wb') as pf:
      pickle.dump(self.geolocation, pf)

  def export(self, **kwargs) -> dict:
    export_data = {
      'modes':     self.modes,
      'mode':      self.mode,
      'last_mode': self.lastMode,
      'address':   self.address,
      'old_address': self.old_address
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
    self.firefly.send_event(event)

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
    self.firefly.send_event(event)
    next_day_event_time = self.getNextDayEvent(day_event)
    scheduler.runAt(next_day_event_time, self.DayEventHandler, day_event=day_event, job_id=day_event)

  def getNextDayEvent(self, day_event):
    now = self.now
    day_event_time = self.geolocation.sun(date=now, local=True).get(day_event)
    if day_event_time is None:
      return False
    if day_event_time < now:
      day_event_time = self.geolocation.sun(date=now + timedelta(days=1), local=True).get(day_event)
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
  def lastMode(self):
    return self._last_mode

  @property
  def isDark(self):
    now = self.now
    sun = self.geolocation.sun(date=now, local=True)
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
        sun = self.geolocation.sun(date=self.now, local=True)
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
    self.firefly.send_event(event)

  def remove_status_message(self, message_id):
    if message_id in self.status_messages:
      self.status_messages.pop(message_id)
      event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, event_action={
        'status_message': 'updated'
      })
      self.firefly.send_event(event)


  def process_command(self, command:Command, **kwargs):
    logging.info('[LOCATION] command: %s' % str(command))
    logging.info('[LOCATION] command: %s args: %s' % (str(command.command), str(command.args)))


    if command.command == 'remove_mode' and command.args.get('mode'):
      self.remove_mode(command.args.get('mode'))
    if command.command == 'add_mode' and command.args.get('mode'):
      self.add_mode(command.args.get('mode'))
    if command.command == 'update_address' and command.args.get('address'):
      self.update_location(command.args.get('address'))

    self.firefly.refresh_firebase()


  @property
  def now(self) -> datetime:
    return datetime.now(self.geolocation.tz)

