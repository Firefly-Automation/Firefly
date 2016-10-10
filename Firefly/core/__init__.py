# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 09:01:35
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-11 09:01:35

ff_zwave = None

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

from core.dispacher.command import sendCommand
from core.dispacher.event import sendEvent
from core.dispacher.request import sendRequest

from core.models.event import Event as ffEvent
from core.models.command import Command as ffCommand

from core.firefly import getDeviceList, getRoutinesList

from core.api.views import *

__all__ = ['sendCommand', 'sendEvent', 'sendRequest', 'ffEvent', 'ffCommand', 'getDeviceList', 'getRoutinesList', 'ffScheduler']