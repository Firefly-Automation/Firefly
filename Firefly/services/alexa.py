from Firefly import logging
from Firefly.helpers.events import Command
from difflib import get_close_matches
from Firefly import aliases
from Firefly.const import TYPE_DEVICE, LEVEL

class AlexaRequest(object):
  def  __init__(self, request: dict):
    self._raw_request = request
    self._slots = {}
    for name, slot in self.request.get('intent', {}).get('slots', {}).items():
      self._slots[name] = AlexaSlot(slot)

  @property
  def type(self):
    return self._raw_request.get('type')

  @property
  def request(self):
    return self._raw_request.get('request', {})

  @property
  def intent(self):
    return self.request.get('intent',{}).get('name')

  @property
  def parameters(self):
    return self._slots


class AlexaSlot(object):
  def __init__(self, slot: dict):
    self.name = slot.get('name')
    self.value = slot.get('value')

def process_alexa_request(firefly, request):
  echo_app_version = 1
  a = AlexaRequest(request)

  return {"version":echo_app_version,"response":alexa_handler(firefly, a)}


def alexa_handler(firefly, request: AlexaRequest):
  devices = [device._alias for _, device in firefly.components.items() if device.type == TYPE_DEVICE]

  if request.intent == 'Switch':
    d = get_close_matches(request.parameters['device'].value, devices)
    if len(d) == 0:
      return make_response('No device found', 'No device found')
    d = d[0]
    ff_id = aliases.get_device_id(d)
    print(request.parameters)
    c = Command(ff_id, 'alexa', request.parameters['state'].value)
    firefly.send_command(c)
    return make_response('Ok', 'Ok')

  if request.intent == 'Dimmer':
    d = get_close_matches(request.parameters['device'].value, devices)
    if len(d) == 0:
      return make_response('No device found', 'No device found')
    d = d[0]
    ff_id = aliases.get_device_id(d)
    print(request.parameters)
    c = Command(ff_id, 'alexa', LEVEL, **{LEVEL: request.parameters['level'].value})
    firefly.send_command(c)
    return make_response('Ok', 'Ok')

  return make_response('Unsupported Command', 'Unsupported Command')








def make_response(output_speech, card_content, output_type="PlainText", card_title="Firefly Smart Home", card_type="Simple", end_session=True):
  response = {"outputSpeech": {"type":output_type,"text":output_speech},"card":{"type":card_type,"title":card_title,"content":card_content},'shouldEndSession':end_session}
  return response