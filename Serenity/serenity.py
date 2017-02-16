from Serenity import firefly_simulate
import json

def firefly_get_request(path):
  if firefly_simulate:
    return_data = ''
    with open(path) as file:
      return_data = json.loads(file.read())
    return return_data
  return {'ERROR':'NOT IMPLEMENTED YET'}
