from Firefly import logging
from Firefly.const import SERVICE_CONFIG_FILE
from Firefly.helpers.service import Service
import configparser
from forecastiopy import ForecastIO, FIOCurrently
from Firefly import scheduler

TITLE = 'Dark Sky Service for Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = 'service_darksky'
COMMANDS = ['refresh']
REQUESTS = ['current']


# TODO: Setup function should get the config from the service config file. If the
# required params are not in the config file then it should log and error message
# and abort install

def Setup(firefly, package, **kwargs):
  config = configparser.ConfigParser()
  config.read(SERVICE_CONFIG_FILE)
  api_key = config.get('DARKSKY','api_key',fallback=None)
  if api_key is None:
    logging.error('DarkSky API key missing')
    return False
  darksky = Darksky(firefly, package, api_key=api_key)
  firefly.components[SERVICE_ID] = darksky
  return True


class Darksky(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self._api_key = kwargs.get('api_key')
    self._long = firefly.location.longitude
    self._lat = firefly.location.latitude
    self._darksky = ForecastIO.ForecastIO(self._api_key,
                                          units=ForecastIO.ForecastIO.UNITS_SI,
                                          lang=ForecastIO.ForecastIO.LANG_ENGLISH,
                                          latitude = self._lat,
                                          longitude= self._long
                                          )
    self._currently = None

    self.add_command('refresh', self.refresh)
    self.add_request('current', self.current)

    scheduler.runEveryM(30, self.refresh)
    self.refresh()

  def refresh(self):
    if self._darksky.has_currently() is True:
      currently = FIOCurrently.FIOCurrently(self._darksky)
      print('Currently')
      for item in currently.get().keys():
        print(item + ' : ' + str(currently.get()[item]))
      # Or access attributes directly
      #print(currently.temperature)
      #print(currently.humidity)
      self._currently = currently
    else:
      print('No Currently data')

  def current(self, command, refresh=False, **kwargs):
    if refresh:
      self.refresh()
    return self._currently

