# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 09:01:35
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-10 22:20:04

class FireflyZwave(object):
  def __init__(self):
    self.zwave = None

ff_zwave = FireflyZwave()

## Import and setup mongo
## Monogo Setup ##
from pymongo import MongoClient

client = MongoClient()
ffDB = client.ff
appsDB = ffDB.apps
datalogDB = ffDB.datalog
deviceDB = ffDB.devices
messageDB = ffDB.message
routineDB = ffDB.routines

datalogDB.ensure_index("timestamp", expireAfterSeconds=(60*60*72))
messageDB.ensure_index("timestamp", expireAfterSeconds=(60*60*24*7))

## SETUP SCHEDULER
from core.scheduler import Scheduler
ffScheduler = Scheduler()

from core.models.command import Command as ffCommand
from core.models.event import Event as ffEvent

from core.dispacher.command import sendCommand
from core.dispacher.event import sendEvent
from core.dispacher.request import sendRequest

## SETUP LOCATION 
from core.utils.location import Location
zipcode = None
modes = None
location_config = 'config/location.json'
with open(location_config) as data_file:
  config = json.load(data_file)
  zipcode = str(config.get('zip_code'))
  modes = config.get('modes')
ffLocation = Location(zipcode, modes)



from core.firefly import getDeviceList, getRoutinesList

from core.api.views import *

__all__ = ['sendCommand', 'sendEvent', 'sendRequest', 'ffEvent', 'ffCommand', 'getDeviceList', 'getRoutinesList', 'ffScheduler', 'ffLocation']


