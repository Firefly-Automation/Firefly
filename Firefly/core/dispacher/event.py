from core import appsDB, deviceDB, routineDB, ff_zwave, ffEvent
import pickle
import logging

def sendEvent(event):
  logging.info('send_event: ' + str(event))

  if event.sendToDevice:
    sendEventToDevice(event)
  
  sendEventToApp(event)
  sendEventToRoutine(event)

def sendEventToRoutine(event):
  for d in  routineDB.find({'listen':event.deviceID}):
    s = pickle.loads(d.get('ffObject'))
    s.event(event)

def sendEventToApp(event):
  for a in appsDB.find({'listen':event.deviceID}):
    app = pickle.loads(a.get('ffObject'))
    app.sendEvent(event)
    appObj = pickle.dumps(app)
    appsDB.update_one({'id':app.id},{'$set': {'ffObject':appObj}, '$currentDate': {'lastModified': True}})

def sendEventToDevice(event):
  for d in deviceDB.find({'id':event.deviceID}):
    s = pickle.loads(d.get('ffObject'))
    s.sendEvent(event)
    d = pickle.dumps(s)
    deviceDB.update_one({'id':event.deviceID},{'$set': {'ffObject':d}, '$currentDate': {'lastModified': True}})
