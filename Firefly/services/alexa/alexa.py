from Firefly import logging
from Firefly.helpers.events import Command
from Firefly import aliases
from difflib import get_close_matches
from Firefly.const import (ACTION_LEVEL, ACTION_OFF, ACTION_ON, ALEXA_OFF_REQUEST, ALEXA_ON_REQUEST,
                           ALEXA_SET_COLOR_REQUEST, ALEXA_SET_COLOR_TEMP_REQUEST, ALEXA_SET_PERCENTAGE_REQUEST,
                           COMMAND_SET_LIGHT, LEVEL, TYPE_AUTOMATION, TYPE_DEVICE)

from Firefly.services.alexa.alexa_const import (DEVICE, DIMMER_INTENT, HELP_INTENT, HELP_RESPONSE, MODE, MODE_INTENT,
                                   REQUEST_SLOT_FILLING, STATE, STOP_INTENT, STOP_RESPONSE, SUPPORTED_INTENTS,
                                   SWITCH_INTENT, UNSUPPORTED_COMMAND, TYPE_LAUNCH, WELCOME_RESPONSE, CANCEL_INTENT, make_response)



def process_alexa_request(firefly, request):
  alexa_request = AlexaRequest(request)

  validate_intent = alexa_request.verify_intent()
  if not validate_intent.valid:
    return validate_intent.response

  alexa_request.process_slots()
  validate_slots = alexa_request.verify_slots()
  if not validate_slots.valid:
    return validate_slots.response

  return alexa_request.process_request(firefly)




class AlexaResponse(object):
  def __init__(self, response={}, code=200, valid=True):
    self.code = 200
    self.response = response
    self.valid = valid

  def make_response(self, output_speech, card_content, output_type="PlainText", card_title="Firefly Smart Home",
                    card_type="Simple", end_session=True):
    self.response = make_response(output_speech, card_content, output_type, card_title, card_type, end_session)
    return self.response


class AlexaSlot(object):
  def __init__(self, slot: dict):
    self.name = slot.get('name')
    self.value = slot.get('value')
    self.confirmation_status = slot.get('confirmationStatus')


class AlexaRequest(object):
  def __init__(self, request):
    self._raw_request = request
    self._slots = {}


  def verify_intent(self):
    if self.intent == STOP_INTENT or self.intent == CANCEL_INTENT:
      return AlexaResponse(STOP_RESPONSE, valid=False)
    if self.intent == HELP_INTENT:
      return AlexaResponse(HELP_RESPONSE, valid=False)
    if self.type == TYPE_LAUNCH:
      return AlexaResponse(WELCOME_RESPONSE, valid=False)
    if self.intent not in SUPPORTED_INTENTS.keys():
      return AlexaResponse(UNSUPPORTED_COMMAND, valid=False)
    return AlexaResponse(valid=True)

  def verify_slots(self):
    for required_value in SUPPORTED_INTENTS[self.intent].get('required'):
      try:
        if self.slots[required_value].value is None:
          return AlexaResponse(REQUEST_SLOT_FILLING, valid=False)
      except:
        return AlexaResponse(REQUEST_SLOT_FILLING, valid=False)

    return AlexaResponse()

  def process_slots(self):
    for name, slot in self.request.get('intent', {}).get('slots', {}).items():
      self._slots[name] = AlexaSlot(slot)

  def process_request(self, firefly):
    logging.info('process_request')

    if self.intent == SWITCH_INTENT:
      devices = [device._alias for _, device in firefly.components.items() if device.type == TYPE_DEVICE]
      d = get_close_matches(self.slots[DEVICE].value, devices)
      if len(d) == 0:
        return make_response('No device found', 'No device found')
      d = d[0]
      ff_id = aliases.get_device_id(d)
      command = Command(ff_id, 'alexa', self.slots[STATE].value)
      firefly.send_command(command)
      return make_response('Ok', 'Ok')


    if self.intent == DIMMER_INTENT:
      devices = [device._alias for _, device in firefly.components.items() if device.type == TYPE_DEVICE]
      d = get_close_matches(self.slots[DEVICE].value, devices)
      if len(d) == 0:
        return make_response('No device found', 'No device found')
      d = d[0]
      ff_id = aliases.get_device_id(d)
      command = Command(ff_id, 'alexa', LEVEL, **{LEVEL: self.slots[STATE].value})
      firefly.send_command(command)
      return make_response('Ok', 'Ok')

    if self.intent == MODE_INTENT:
      routines = {}
      for id, c in firefly.components.items():
        if c.type == TYPE_AUTOMATION and 'routine' in c._package:
          routines[c._alias] = id
      r_alias = get_close_matches(self.slots[MODE].value, routines.keys())
      if len(r_alias) == 0:
        return make_response('Routine not found', 'Routine not found')
      r_alias = r_alias[0]
      r = routines[r_alias]
      c = Command(r, 'alex', 'execute')
      firefly.send_command(c)
      return make_response('Ok', 'Ok')

  @property
  def slots(self):
    return self._slots

  @property
  def type(self):
    return self._raw_request.get('type')

  @property
  def request(self):
    return self._raw_request #.get('request', {})

  @property
  def intent(self):
    return self.request.get('intent', {}).get('name')

  @property
  def parameters(self):
    return self._slots

  @property
  def dialog_state(self):
    return self.request.get('dialogState')
