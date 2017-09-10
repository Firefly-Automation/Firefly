from openzwave.network import ZWaveNode

from Firefly import logging, scheduler
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ALEXA_OFF, ALEXA_ON, ALEXA_SET_PERCENTAGE, COMMAND_SET_LIGHT, DEVICE_TYPE_DIMMER, EVENT_ACTION_OFF, EVENT_ACTION_ON, LEVEL, STATE, SWITCH
from Firefly.helpers.metadata import metaDimmer, metaSwitch

TITLE = 'Aeotec ZW111 Dimmer'
DEVICE_TYPE = DEVICE_TYPE_DIMMER
AUTHOR = 'Zachary Priddy'
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, LEVEL, COMMAND_SET_LIGHT]
REQUESTS = [STATE, LEVEL]
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF,
  '_level': 0
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_switch = ZW111(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_switch.id] = new_switch
  return new_switch.id


class ZW111(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self._dimmers = None
    self._switches = None
    self._done_sending_command = True

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)
    self.add_command(LEVEL, self.set_level)
    self.add_command(COMMAND_SET_LIGHT, self.set_light)

    self.add_action(STATE, metaSwitch(primary=True))
    self.add_action(LEVEL, metaDimmer())

    self.add_request(STATE, self.get_state)
    self.add_request(SWITCH, self.get_state)
    self.add_request(LEVEL, self.get_level)

    self.add_alexa_action(ALEXA_OFF)
    self.add_alexa_action(ALEXA_ON)
    self.add_alexa_action(ALEXA_SET_PERCENTAGE)

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    if node is None:
      return

    super().update_from_zwave(node, **kwargs)

    values = kwargs.get('values')
    if values is None:
      return
    genre = values.genre
    if genre != 'User':
      return

    self._dimmers = list(self._node.get_dimmers().keys())
    self._switches = list(self._node.get_switches_all().keys())

    self._level = node.get_dimmer_level(self._dimmers[0])

    if self._done_sending_command:
      self._state = EVENT_ACTION_ON if self._node.get_switch_all_state(self._switches[0]) else EVENT_ACTION_OFF

  def set_light(self, **kwargs):
    self.set_level(**kwargs)

  def set_level(self, **kwargs):
    level = 100
    try:
      level = int(kwargs.get('level', 100))
    except Exception as e:
      logging.error('[GE DIMMER] Error parsing level.')

    if self.node is None:
      logging.error('[GE Dimmer] Node is not set yet.')
      return
    self._node.set_dimmer(self._dimmers[0], level)
    self._node.set_switch_all(self._switches[0], 1 if level > 0 else 0)
    self._level = level
    self._state = EVENT_ACTION_OFF if self._level == 0 else EVENT_ACTION_ON
    # self._state = EVENT_ACTION_ON if self._node.get_switch_all_state(self._switches[0]) else EVENT_ACTION_OFF

  def off(self, **kwargs):
    self.member_set('_state', EVENT_ACTION_OFF)
    self._done_sending_command = False
    scheduler.runInS(5, self.set_done_sending_command, job_id='set_command')

    self._node.set_dimmer(self._dimmers[0], 0)
    self._node.set_switch_all(self._switches[0], 0)
    self._state = EVENT_ACTION_OFF
    return EVENT_ACTION_OFF

  def set_done_sending_command(self, **kwargs):
    self._done_sending_command = True

  def on(self, **kwargs):
    self.member_set('_state', EVENT_ACTION_ON)
    self._done_sending_command = False
    scheduler.runInS(5, self.set_done_sending_command, job_id='set_command')

    self._node.set_dimmer(self._dimmers[0], 255)
    self._node.set_switch_all(self._switches[0], 1)
    self._level = self._node.get_dimmer_level(self._dimmers[0])
    self._state = EVENT_ACTION_ON
    return EVENT_ACTION_ON

  def toggle(self, **kwargs):
    if self.state == EVENT_ACTION_ON:
      return self.off()
    return self.on()

  def get_state(self, **kwargs):
    return self.state

  def get_level(self, **kwargs):
    return self.level

  @property
  def level(self):
    return self._level

  @property
  def state(self):
    return self._state
