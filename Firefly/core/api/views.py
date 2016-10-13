import json

from core import getRoutineList
from core.firefly import app
from flask import Flask

@app.route('/')
def baseView():
  return "This is the root page"

@app.route('/API/core/views/routine'):
def APICoreViewRoutine():
  routine_list = getRoutineList()
  return_data = {}
  for r in routine_list:
    if r.get('icon') is None:
      continue
    rID = r .get('id')
    return_data[rID] = {'id': rID, 'icon':r.get('icon')}

  logging.debug(str(return_data))
  return json.dumps(return_data, sort_keys=True)