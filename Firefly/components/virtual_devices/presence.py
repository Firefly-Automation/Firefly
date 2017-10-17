from Firefly import logging, scheduler
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import (ACTION_SET_DELAY, ACTION_SET_PRESENCE, DEVICE_TYPE_PRESENCE, NOT_PRESENT, PRESENCE, PRESENT)
from Firefly.helpers.action import Command
from Firefly.helpers.device import Device
from Firefly.helpers.metadata import metaOwntracks, metaPresence, metaQR, metaText, action_presence

TITLE = 'Firefly Virtual Presence Device'
DEVICE_TYPE = DEVICE_TYPE_PRESENCE
AUTHOR = AUTHOR
COMMANDS = [ACTION_SET_DELAY, ACTION_SET_PRESENCE]
REQUESTS = [PRESENCE, 'zone', 'firebase_api_key']
INITIAL_VALUES = {
  '_delay':           5,
  '_presence':        NOT_PRESENT,
  '_lat':             0,
  '_lon':             0,
  '_beacon_presence': NOT_PRESENT,
  '_geo_presence':    NOT_PRESENT,
  '_zone':            ''
}


def Setup(firefly, package, **kwargs):
  """

  Args:
      firefly:
      package:
      kwargs:
  """
  logging.message('Entering %s setup' % TITLE)
  new_presence = VirtualPresence(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_presence.id] = new_presence


class VirtualPresence(Device):
  """
  """

  def __init__(self, firefly, package, **kwargs):
    """

    Args:
        firefly:
        package:
        kwargs:
    """
    if kwargs.get('initial_values'):
      INITIAL_VALUES.update(kwargs.get('initial_values'))
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self.add_command(ACTION_SET_PRESENCE, self.set_presence)
    self.add_command(ACTION_SET_DELAY, self.set_delay)

    self.add_request(PRESENCE, self.get_presence)
    self.add_request('zone', self.get_zone)
    self.add_request('firebase_api_key', self.get_firebase_api_key)

    self.add_action(PRESENCE, action_presence())
    self.add_action('presenceText', metaText(title='Presence New', text_request=PRESENCE, context='Presence of the device.'))
    self.add_action('zone', metaText(title='Current Zone', text_request='zone', context='Current Zone'))

    beacon = self.firefly.beacon_id
    if beacon is not None:
      beacon = beacon.replace(' ', '')
      beacon = '%s-%s-%s-%s-%s' % (beacon[0:8], beacon[8:12], beacon[12:16], beacon[16:20], beacon[20:])
      qr_data = 'owntracks:///beacon?name=-Firefly-Home-Beacon&uuid=%s&major=1&minor=1' % beacon
      self.add_action('qr', metaQR(data=qr_data, title='OwnTracks QR (iOS)'))

    # TODO: Make HOMEKIT CONST
    self.add_homekit_export('HOMEKIT_PRESENCE', PRESENCE)

    self._alexa_export = False

    self.firebase_api_key = kwargs.get('firebase_api_key', None)
    if self.firebase_api_key is None and self.firefly.firebase_enabled:
      self.register_firebase()

    ownTracksData = {
      "_type": "configuration",
      "auth":  False,
      "host":  "https://us-central1-firefly-beta-cdb9d.cloudfunctions.net/ownTracksApi?ff_id=%s&key=%s" % (self.id, self.firebase_api_key),
      "url":   "https://us-central1-firefly-beta-cdb9d.cloudfunctions.net/ownTracksApi?ff_id=%s&key=%s" % (self.id, self.firebase_api_key),
      "port":  443,
    }

    self.add_action('owntracks', metaOwntracks(data=ownTracksData, title="OwnTracks Config (iOS)",
                                               context="Its best to download this on a computer and email it to your phone. You should be able to open it on your phone and owntracks will open. "
                                                       "After this is done use the import beacon button below  from the web browser."))

    waypoints = [{
      '_type': 'waypoint',
      'uuid':  beacon,
      'major': 1,
      'minor': 1,
      'lat':   0,
      'lon':   0,
      'desc':  '-Firefly-Home-Beacon',
      'tst':   int(self.firefly.location.now.timestamp())
    }]

    ownTracksBeaconData = ownTracksData.copy()
    ownTracksBeaconData.pop('host')
    ownTracksBeaconData.pop('auth')
    ownTracksBeaconData.pop('port')
    ownTracksBeaconData['waypoints'] = waypoints

    self.add_action('owntracksWaypoint', metaOwntracks(data=ownTracksBeaconData, title='OwnTracks Config (Android) Download and open with OwnTracks (waypoints may not be shown)',
                                                       context="Beacon: %s | major: 1 | minor: 1 | lat: 0 | lon: 0 | name: -Firefly-Home-Beacon" % beacon))

  def export(self, current_values: bool = True, api_view: bool = False):
    export_data = super().export(current_values, api_view)
    export_data['firebase_api_key'] = self.firebase_api_key
    return export_data

  def set_presence(self, **kwargs):
    """

    Args:
        kwargs:
    """

    logging.info(kwargs)

    lat = kwargs.get('lat')
    lon = kwargs.get('lon')
    presence = kwargs.get('presence')
    beacon_presence = kwargs.get('beacon_presence')
    zone = kwargs.get('zone')

    try:
      if lat is not None and lon is not None:
        self._lat = float(lat)
        self._lon = float(lon)
    except Exception as e:
      # TODO: Generate error code.
      logging.error('error setting lat and lon: %s' % e)

    if zone is not None:
      if 'firefly-home' in zone.lower():
        if presence is not None:
          self.set_geo_presence(presence)
        if beacon_presence is not None:
          self.set_beacon_presence(beacon_presence)
      else:
        presence = PRESENT if (presence == PRESENT or beacon_presence == PRESENT) else NOT_PRESENT
        self.set_zone(presence, zone)

    self.check_presence()

  def set_geo_presence(self, presence):
    if presence == PRESENT:
      scheduler.cancel(job_id='%s_set_geo_presence' % self.id)
      self._geo_presence = PRESENT
      self.check_presence()
    else:
      scheduler.runInM(self._delay, self.set_geo_not_present, job_id='%s_set_geo_presence' % self.id)

  def set_geo_not_present(self):
    self.member_set('_geo_presence', NOT_PRESENT)
    self.check_presence()

  def set_beacon_presence(self, presence):
    if presence == PRESENT:
      scheduler.cancel('%s_set_beacon_presence' % self.id)
      self._beacon_presence = PRESENT
      self.check_presence()
    else:
      scheduler.runInM(self._delay, self.set_beacon_not_present, job_id='%s_set_beacon_presence' % self.id)

  def set_beacon_not_present(self):
    self.member_set('_beacon_presence', NOT_PRESENT)
    self.check_presence()

  def set_zone(self, presence, zone):
    if presence == PRESENT:
      self._zone = zone
    else:
      self.member_set('_zone', 'Not inside of zone.')

  def check_presence(self):
    """ Check both geo_presence and beacon_presence and set device presence based on the OR of the two.

    """
    presence = PRESENT if (self._beacon_presence == PRESENT or self._geo_presence == PRESENT) else NOT_PRESENT
    if presence == PRESENT:
      self._presence = PRESENT
    else:
      self.member_set('_presence', NOT_PRESENT)
    self.set_zone(presence, 'Home')

  def set_delay(self, **kwargs):
    """ Set the delay to before setting not_present.

    Args:
        kwargs:
          delay: (int) delay in minutes.
    """
    delay = int(kwargs.get('delay', 5))
    self._delay = delay

  def register_firebase(self):
    """ Create a Firebase API token for this device for reporting presence.

    """
    # TODO: Generate config file if there is a beaconID set. This will allow us to download a config file in the future.
    command = Command('service_firebase', self.id, 'get_api_id', callback=self.set_firebase_api_key, api_ff_id=self.id)
    self.firefly.send_command(command)

  def set_firebase_api_key(self, **kwargs):
    """ Callback function for registering the device to firebase.

    Args:
      firebase_api_key: (str) firebase key.
    """
    self.firebase_api_key = kwargs.get('firebase_api_key')
    ownTracksData = {
      "_type": "configuration",
      "auth":  False,
      "host":  "https://us-central1-firefly-beta-cdb9d.cloudfunctions.net/ownTracksApi?ff_id=%s&key=%s" % (self.id, self.firebase_api_key),
      "port":  443,
    }

    self.add_action('owntracks', metaOwntracks(data=ownTracksData))

  def get_firebase_api_key(self) -> str:
    """ Gets the firebase api key.

    Returns: firebase api key.

    """
    return str(self.firebase_api_key)

  def get_presence(self) -> str:
    """ Gets the presence if the device.

    Returns: (str) presence string.

    """
    return self._presence

  def get_zone(self) -> str:
    """ Gets the zone the device is in.

    Returns: (str) zone string.

    """
    return self._zone

  def get_location(self) -> dict:
    """ Gets the lat lon of the device.

    Returns: (dict) lat and lon of device.

    """
    return {
      'lat': self._lat,
      'lon': self._lon
    }
