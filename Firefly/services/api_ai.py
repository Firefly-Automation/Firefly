from Firefly import logging
from Firefly.helpers.events import Command
from difflib import get_close_matches
from Firefly import aliases
from Firefly.const import TYPE_DEVICE, LEVEL

def process_api_ai_request(firefly, request):
  a = APIaiRequest(request)
  devices = [device._alias for _, device in firefly.components.items() if device.type == TYPE_DEVICE]
  rooms = [device._alias for _, device in firefly.components.items() if device.type == 'ROOM']


  if a.intent == 'firefly.simple_action':
    for device in a.parameters.devices:
      d = get_close_matches(device, devices)
      if len(d) == 0:
        error = 'No device found matching name %s' % device
        return make_response(all=error)
      d = d[0]
      ff_id = aliases.get_device_id(d)
      c = Command(ff_id, 'api_ai', a.parameters.command)
      firefly.send_command(c)
    return make_response(all='Ok')

  if a.intent == 'firefly.list_devices':
    device_list = '\n'.join(list(devices))
    return make_response(text=device_list, slack=device_list, speech='Ok')

  if a.intent == 'firefly.dim_lights':
    for device in a.parameters.devices:
      print(device)
      d = get_close_matches(device, devices)
      if len(d) == 0:
        error = 'No device found matching name %s' % device
        return make_response(all=error)
      d = d[0]
      ff_id = aliases.get_device_id(d)
      c = Command(ff_id, 'api_ai', LEVEL, **{LEVEL:a.parameters.level})
      print(c)
      firefly.send_command(c)
    return make_response(all='Ok')

  if a.intent == 'firefly.room_simple':
    room = a.parameters.room
    r = get_close_matches(room, rooms)
    if len(r) == 0:
      error = 'No room found matching name %s' % room
      return make_response(all=error)
    r = r[0]
    ff_id = aliases.get_device_id(r)
    c = Command(ff_id, 'api_ai', a.parameters.command, tags=a.parameters.tags)
    firefly.send_command(c)
    return make_response(all='Ok')

  return make_response(all='Unsupported Command')






def make_response(speech='', text='', slack='', all=None, source='Firefly'):
  if all:
    speech = all
    text = all
    slack = all

  return {
    'speech': speech,
    'source': source,
    'displayText': text,
    'data': {
      'slack': {
        'text': slack
      }
    },
    'contextOut': []
  }



class APIaiParameters(object):
  def __init__(self, request):
    self._parameters = self._result = request.get('result', {}).get('parameters', {})

  def __str__(self):
    return str(self.__dict__)

  @property
  def action(self):
    return self._parameters.get('action')

  @property
  def command(self):
    return self.action.get('action')

  @property
  def level(self):
    return int(self._parameters.get('level', 100))

  @property
  def command_type(self):
    return self.action.get('action_type')

  @property
  def room(self):
    return self._parameters.get('room')

  @property
  def tags(self):
    return self._parameters.get('tags')

  @property
  def devices(self):
    return self._parameters.get('firefly_devices')


class APIaiMetadata(object):
  def __init__(self, request):
    self._metadata = self._result = request.get('result', {}).get('metadata', {})

  @property
  def intent(self):
    return self._metadata.get('intentName')


class APIaiRequest(object):
  def __init__(self, request):
    self._raw_request = request.copy()
    self._result = request.get('result', {})
    self._metadata = APIaiMetadata(request)
    self._parameters = APIaiParameters(request)


  @property
  def intent(self):
    return self.metadata.intent

  @property
  def metadata(self) -> APIaiMetadata:
    return self._metadata

  @property
  def parameters(self) -> APIaiParameters:
    return self._parameters

  @property
  def raw(self):
    return self._raw_request