from Firefly import logging, scheduler
from Firefly.const import AUTHOR
from Firefly.helpers.device import Device
from Firefly.helpers.metadata import ColorMap, action_text
from .foobot_service import STATUS_URL
import requests

TITLE = 'Foobot Air Sensor'
DEVICE_TYPE = 'air_sensor'
REQUESTS = ['air_quality', 'pm', 'temperature', 'humidity', 'c02', 'voc', 'allpollu']
COMMANDS = ['set_temp_scale']

INITIAL_VALUES = {
  'air_quality':  'unknown',
  '_pm':          -1,
  '_temperature': -1,
  '_humidity':    -1,
  '_c02':         -1,
  '_voc':         -1,
  '_allpollu':    -1,
  '_temp_scale': 'f'
}

SCORE_MAP = {
  0: 'great',
  1: 'good',
  2: 'fair',
  3: 'poor',
  100: 'unknown'
}

'''
Sample response:
{
  "uuid": "XXXXXXXXXX",
  "start": 1508214354,
  "end": 1508214354,
  "sensors": [
    "time",
    "pm",
    "tmp",
    "hum",
    "co2",
    "voc",
    "allpollu"
  ],
  "units": [
    "s",
    "ugm3",
    "C",
    "pc",
    "ppm",
    "ppb",
    "%"
  ],
  "datapoints": [
    [
      1508214354,
      2.5200195,
      23.761,
      50.453,
      451,
      125,
      2.5200195
    ]
  ]
}
'''


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  foobot = Foobot(firefly, package, **kwargs)
  firefly.components[foobot.id] = foobot


class Foobot(Device):
  def __init__(self, firefly, package, **kwargs):
    initial_values = kwargs.get('initial_values', {})
    INITIAL_VALUES.update(initial_values)
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)

    # ff_id will be the uuid of the device
    self.device = kwargs.get('foobot_device')
    self.api_key = kwargs.get('api_key')
    self.username = kwargs.get('username')
    self.refresh_interval = kwargs.get('refresh_interval')

    self.add_request('air_quality', self.get_air_quality)
    self.add_request('temperature', self.get_temperature)
    self.add_request('humidity', self.get_humidity)
    self.add_request('pm', self.get_pm)
    self.add_request('c02', self.get_c02)
    self.add_request('voc', self.get_voc)
    self.add_request('allpillu', self.get_allpollu)

    self.add_command('set_temp_scale', self.set_scale)

    text_mapping = {
      'Great':      ['great'],
      'Good':       ['good'],
      'Fair':       ['fair'],
      'Poor':       ['poor'],
      'No Reading': ['unknown']
    }
    color_mapping = ColorMap(green=['great'], orange=['good'], yellow=['fair'], red=['poor'], black=['unknown'])
    self.add_action('air_quality', action_text(primary=True, title='Air Quality', context='Calculated Air Quality', request='Air Quality', text_mapping=text_mapping, color_mapping=color_mapping))

    self.update()
    scheduler.runEveryM(self.refresh_interval, self.update, job_id=self.id)


  def set_scale(self, **kwargs):
    scale = kwargs.get('scale', 'f')
    if scale == 'f' or scale =='c':
      self._temp_scale = scale

  def get_air_quality(self, **kwargs):
    score = max([self.voc_score(), self.c02_score(), self.pm_score()])
    return SCORE_MAP[score]

  def get_pm(self, **kwargs):
    return self._pm

  def get_temperature(self, **kwargs):
    if self._temp_scale == 'c':
      return self._temperature
    return 9.0/5.0 * self._temperature + 32

  def get_humidity(self, **kwargs):
    return self._humidity

  def get_c02(self, **kwargs):
    return self._co2

  def get_voc(self, **kwargs):
    return self._voc

  def get_allpollu(self, **kwargs):
    return self._allpollu

  def update(self, **kwargs):
    url = STATUS_URL % str(self.id)
    headers = {
      'X-API-KEY-TOKEN': self.api_key,
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
      logging.message('[FOOBOT] Error refreshing: %s' % r.text)

    data = r.json()

    logging.info('[FOOBOT] data: %s' % str(data))

    datapoints = data.get('datapoints')
    if not datapoints:
      return
    datapoints = datapoints[0]
    if len(datapoints) < 7:
      return

    self._pm = datapoints[1]
    self._temperature = datapoints[2]
    self._humidity = datapoints[3]
    self._c02 = datapoints[4]
    self._voc = datapoints[5]
    self._allpollu = datapoints[6]


  def pm_score(self, **kwargs):
    if self._pm == -1:
      return 100
    if self._pm <= 12.5:
      return 0
    if self._pm <= 25:
      return 1
    if self._pm <=37.5:
      return 2
    return 3

  def voc_score(self, **kwargs):
    if self._voc == -1:
      return 100
    if self._voc <= 150:
      return 0
    if self._voc <= 300:
      return 1
    if self._voc <= 450:
      return 2
    return 3

  def c02_score(self, **kwargs):
    if self._c02 == -1:
      return 100
    if self._c02 <= 625:
      return 0
    if self._c02 <= 1300:
      return 1
    if self._c02 <= 1925:
      return 2
    return 3


