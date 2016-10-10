import logging
import pickle

from core import appsDB, deviceDB, ffCommand, routineDB

def sendCommand(command):
  from core import ff_zwave
  logging.info("sendCommand: " + str(command))
  if command.routine:
    return sendRoutineCommand(command)

  if ff_zwave.zwave is not None:
    if command.deviceID == ff_zwave.name:
      ff_zwave.zwave.sendCommand(command)
      return True

  if ff_zwave is None:
    logging.critical('-------------------ZWAVE IS NONE--------------------')


  #TODO: Have option in command for device/app
  success = False
  success = success or sendDeviceCommand(command)
  success = success or sendAppCommand(command)
  return success

def sendDeviceCommand(command):
  success = False
  for d in deviceDB.find({'id':command.deviceID}):
    s = pickle.loads(d.get('ffObject'))
    s.sendCommand(command)
    d = pickle.dumps(s)
    deviceDB.update_one({'id':command.deviceID},{'$set': {'ffObject':d}, '$currentDate': {'lastModified': True}})
  return success

def sendRoutineCommand(command):
  routine = routineDB.find_one({'id':command.deviceID})
  if routine:
    r = pickle.loads(routine.get('ffObject'))
    r.executeRoutine(force=command.force)
    return True
  return False

def sendAppCommand(command):
  success = False
  for a in appsDB.find({'id':command.deviceID}):
    app = pickle.loads(a.get('ffObject'))
    app.sendCommand(command)
    appObj = pickle.dumps(app)
    appsDB.update_one({'id':app.id},{'$set': {'ffObject':appObj}, '$currentDate': {'lastModified': True}})
    success = True
  return success