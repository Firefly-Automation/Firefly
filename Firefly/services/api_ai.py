from difflib import get_close_matches

from Firefly import aliases
from Firefly.const import LEVEL, TYPE_AUTOMATION, TYPE_DEVICE, COMMAND_SET_LIGHT
from Firefly.helpers.events import Command


class NoDeviceFound(Exception):
  pass


def get_device_id(firefly, device_alias):
  devices = [device._alias for _, device in firefly.components.items() if device.type == TYPE_DEVICE]
  d = get_close_matches(device_alias, devices)
  if len(d) == 0:
    error = 'No device found matching name %s' % device_alias
    raise NoDeviceFound(error)
  d = d[0]
  ff_id = aliases.get_device_id(d)
  return ff_id


def get_routine_id(firefly, routine_alias):
  routines = {}
  for id, c in firefly.components.items():
    if c.type == TYPE_AUTOMATION and 'routine' in c._package:
      routines[c._alias] = id
  r_alias = get_close_matches(routine_alias, routines.keys())
  if len(r_alias) == 0:
    error = 'No device found matching name %s' % routine_alias
    raise NoDeviceFound(error)
  r_alias = r_alias[0]
  r = routines[r_alias]
  return r


# TODO: Rename these api_ai
def apiai_command_reply(firefly, message):
  try:
    print('************ API AI **************')
    print(str(message))
    command = message.get('command')
    if command == 'switch':
      return apiai_switch(firefly, message)
    if command == 'routine':
      return apiai_routine(firefly, message)
    if command == 'level':
      return apiai_level(firefly, message)
  except:
    pass

  return {
    'text':   'Unknown error',
    'speech': 'Unknown error'
  }


def apiai_switch(firefly, message):
  try:
    devices = [get_device_id(firefly, d) for d in message.get('firefly_devices')]
  except NoDeviceFound as e:
    return {
      'text':   e,
      'speech': e
    }
  except:
    return {
      'text':   'Unknown error',
      'speech': 'Unknown error'
    }
  switch_action = message.get('firefly_switch_action')
  for d in devices:
    c = Command(d, 'api_ai', switch_action)
    firefly.send_command(c)
  return {
    'text':   'Okay',
    'speech': 'Okay'
  }

def apiai_level(firefly, message):
  try:
    devices = [get_device_id(firefly, d) for d in message.get('firefly_devices')]
  except NoDeviceFound as e:
    return {
      'text':   e,
      'speech': e
    }
  except Exception as e:
    return {
      'text':   e,
      'speech': e
    }
  level = int(message.get('level'))
  for d in devices:
    c = Command(d, 'api_ai', COMMAND_SET_LIGHT, level=level)
    firefly.send_command(c)
  return {
    'text':   'Okay',
    'speech': 'Okay'
  }


def apiai_routine(firefly, message):
  routine = message.get('mode')
  try:
    r = get_routine_id(firefly, routine)
  except NoDeviceFound as e:
    return {
      'text':   e,
      'speech': e
    }
  except:
    return {
      'text':   'Unknown error',
      'speech': 'Unknown error'
    }
  c = Command(r, 'api_ai', 'execute')
  firefly.send_command(c)
  return {
    'text':   'Okay',
    'speech': 'Okay'
  }


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
      c = Command(ff_id, 'api_ai', LEVEL, **{
        LEVEL: a.parameters.level
      })
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

  if a.intent == 'firefly.add_zwave':
    ff_id = 'service_zwave'
    c = Command(ff_id, 'api_ai', 'add_node')
    firefly.send_command(c)
    return make_response(all='Ready to pair. Please press the pair button on your zwave device.')

  if a.intent == 'firefly.add_rule.motion':  # Only works with room action
    print('***************************************')
    print(a.parameters.action)
    print(a.parameters.room)
    print(a.parameters.duration)  # TIME
    print(a.parameters.tags)  # MOTION ACTIVE IN ACTIVE
    print(a.parameters.trigger_action)  # ROOM
    print('***************************************')

    room = a.parameters.room
    r = get_close_matches(room, rooms)
    if len(r) == 0:
      error = 'No room found matching name %s' % room
      return make_response(all=error)
    r = r[0]
    room_ff_id = aliases.get_device_id(r)
    first_action = a.parameters.action.get('action')
    delayed_action = 'off' if a.parameters.action.get('action') == 'on' else 'on'

    actions = [{
      "command":    first_action,
      "conditions": {
      },
      "ff_id":      room_ff_id,
      "force":      False,
      "source":     "api_ai_automation",
      "tags":       [a.parameters.tags]
    }]

    delayed_actions = [{
      "command":    delayed_action,
      "conditions": {
      },
      "ff_id":      room_ff_id,
      "force":      False,
      "source":     "api_ai_automation",
      "tags":       [a.parameters.tags]
    }]

    trigger = a.parameters.trigger_action.get('action')
    delayed_trigger = 'inactive' if a.parameters.trigger_action.get('action') == 'active' else 'active'
    triggers = [[{
      "event_action": [{
        "motion": [trigger]
      }],
      "listen_id":    room_ff_id,
      "source":       "SOURCE_TRIGGER"
    }]]

    delayed_triggers = [[{
      "event_action": [{
        "motion": [delayed_trigger]
      }],
      "listen_id":    room_ff_id,
      "source":       "SOURCE_TRIGGER"
    }]]

    new_automation = {
      "actions":          actions,
      "alias":            "api_ai_automation",
      "conditions":       {},
      "delayed_actions":  delayed_actions,
      "delayed_triggers": delayed_triggers,
      "ff_id":            "api_ai_automation",
      "initial_values":   "TODO INITIAL VALUES",
      "package":          "Firefly.automation.event_based_action",
      "triggers":         triggers,
      "type":             "TYPE_AUTOMATION"
    }

    if type(a.parameters.duration) is not dict:
      new_automation.update({
        'delay_s': 10
      })
    elif a.parameters.duration.get('unit') == 'min':
      new_automation.update({
        'delay_m': a.parameters.duration.get('amount')
      })
    elif a.parameters.duration.get('unit') == 's':
      new_automation.update({
        'delay_s': a.parameters.duration.get('amount')
      })
    elif a.parameters.duration.get('unit') == 'h':
      new_automation.update({
        'delay_h': a.parameters.duration.get('amount')
      })
    else:
      new_automation.update({
        'delay_s': 10
      })

    print(new_automation)
    firefly.install_package('Firefly.automation.event_based_action', **new_automation)

    return make_response(all='Okay. I will try to do that')

  return make_response(all='Unsupported Command')


'''
***************************************
{'action': 'on', 'action_type': 'switch'}
kitchen
-1
light
{'action': 'active'}
***************************************
'''


def make_response(speech='', text='', slack='', all=None, source='Firefly'):
  if all:
    speech = all
    text = all
    slack = all

  return {
    'speech':      speech,
    'source':      source,
    'displayText': text,
    'data':        {
      'slack': {
        'text': slack
      }
    },
    'contextOut':  []
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
  def action_devices(self):
    return self._parameters.get('action_devices')

  @property
  def trigger_devices(self):
    return self._parameters.get('trigger_devices')

  @property
  def trigger_action(self):
    return self._parameters.get('trigger_action')

  @property
  def trigger_type(self):
    return self._parameters.get('trigger_type')

  @property
  def duration(self):
    return self._parameters.get('duration')

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
