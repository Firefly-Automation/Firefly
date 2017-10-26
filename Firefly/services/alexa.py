from difflib import get_close_matches
from Firefly import logging

from Firefly import aliases
from Firefly.const import (ACTION_LEVEL, ACTION_OFF, ACTION_ON, ALEXA_OFF_REQUEST, ALEXA_ON_REQUEST,
                           ALEXA_SET_COLOR_REQUEST, ALEXA_SET_COLOR_TEMP_REQUEST, ALEXA_SET_PERCENTAGE_REQUEST,
                           COMMAND_SET_LIGHT, LEVEL, TYPE_AUTOMATION, TYPE_DEVICE)
from Firefly.helpers.events import Command


class AlexaRequest(object):
  def __init__(self, request: dict):
    logging.debug('[ALEXA REQUEST] request: %s' % str(request))

    self._raw_request = request
    self._slots = {}
    for name, slot in self.request.get('intent', {}).get('slots', {}).items():
      self._slots[name] = AlexaSlot(slot)

    logging.debug('[ALEXA REQUEST] intent: %s' % str(self.intent))

  @property
  def type(self):
    return self._raw_request.get('type')

  @property
  def request(self):
    return self._raw_request if self._raw_request else {}

  @property
  def intent(self):
    return self.request.get('intent', {}).get('name')

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

  return {
    "version":  echo_app_version,
    "response": alexa_handler(firefly, a)
  }


def alexa_handler(firefly, request: AlexaRequest):
  devices = [device._alias for _, device in firefly.components.items() if device.type == TYPE_DEVICE]

  logging.debug('[ALEXA HANDLER] intent: %s' % str(request.intent))


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
    c = Command(ff_id, 'alexa', LEVEL, **{
      LEVEL: request.parameters['level'].value
    })
    firefly.send_command(c)
    return make_response('Ok', 'Ok')

  if request.intent == 'ChangeMode':
    routines = {}
    for id, c in firefly.components.items():
      if c.type == TYPE_AUTOMATION and 'routine' in c._package:
        routines[c._alias] = id
    r_alias = get_close_matches(request.parameters['mode'].value, routines.keys())
    if len(r_alias) == 0:
      return make_response('Routine not found', 'Routine not found')
    r_alias = r_alias[0]
    r = routines[r_alias]
    c = Command(r, 'alex', 'execute')
    firefly.send_command(c)
    return make_response('Ok', 'Ok')

  return make_response('Unsupported Command', 'Unsupported Command')


def make_response(output_speech, card_content, output_type="PlainText", card_title="Firefly Smart Home",
                  card_type="Simple", end_session=True):
  response = {
    "outputSpeech":     {
      "type": output_type,
      "text": output_speech
    },
    "card":             {
      "type":    card_type,
      "title":   card_title,
      "content": card_content
    },
    'shouldEndSession': end_session
  }
  return response


class AlexaHomeResponse(object):
  def __init__(self, success=True, payload={}):
    self.success = success
    self.payload = payload


class AlexaHomeRequest(object):
  def __init__(self, data: dict = {}):
    self.ff_id = data.get('ff_id')
    self.command = data.get('command')
    self.payload = data.get('payload')

  def process_command(self, firefly):
    # TODO: ADD REAL LOGIC
    try:
      command = None
      response = AlexaHomeResponse()
      if self.command == ALEXA_OFF_REQUEST:
        command = Command(self.ff_id, 'alexa_smart_home', ACTION_OFF)
      elif self.command == ALEXA_ON_REQUEST:
        command = Command(self.ff_id, 'alexa_smart_home', ACTION_ON)
      elif self.command == ALEXA_SET_PERCENTAGE_REQUEST:
        level = self.payload.get('percentageState').get('value')
        command = Command(self.ff_id, 'alexa_smart_home', ACTION_LEVEL, level=level)
      elif self.command == ALEXA_SET_COLOR_TEMP_REQUEST:
        ct = self.payload.get('colorTemperature').get('value')
        command = Command(self.ff_id, 'alexa_smart_home', COMMAND_SET_LIGHT, ct=str(ct) + 'K')
        response.payload = {
          'achievedState': {
            'colorTemperature': {
              'value': ct
            }
          }
        }
      elif self.command == ALEXA_SET_COLOR_REQUEST:
        color_settings = self.payload.get('color')
        hue = color_settings.get('hue')
        sat = color_settings.get('saturation')
        bri = color_settings.get('brightness')
        command = Command(self.ff_id, 'alexa_smart_home', COMMAND_SET_LIGHT, alexa={
          'hue': hue,
          'bri': bri,
          'sat': sat
        })
        response.payload = {
          'achievedState': {
            'color': color_settings
          }
        }

      if command:
        firefly.send_command(command)
        return response

      response.success = False
      response.payload = {
        'error': 'command not found'
      }
      return False
    except Exception as e:
      return AlexaHomeResponse(False, {
        'error': str(e)
      })
