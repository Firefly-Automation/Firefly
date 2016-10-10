from core.models.request import Request
from core import deviceDB
import pickle
import logging

def sendRequest(request):
  logging.debug('send_request' + str(request))
  d = deviceDB.find_one({'id':request.deviceID})
  if d:
    if not request.forceRefresh:
      if request.all or request.multi:
        return d.get('status')
      else:
        return d.get('status').get(request.request)
    else:
      device = pickle.loads(d.get('ffObject'))
      data = device.requestData(request)
      return data
  return None