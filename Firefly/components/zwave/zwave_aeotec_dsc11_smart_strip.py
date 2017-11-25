from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import ACTION_OFF, ACTION_ON, ACTION_TOGGLE, DEVICE_TYPE_SWITCH, EVENT_ACTION_OFF, EVENT_ACTION_ON, STATE
from Firefly.helpers.metadta.metadata import metaSwitch

TITLE = 'Firefly Aeotec SDSC11 Smart Strip'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, 'switch1', 'switch2', 'switch3', 'switch4', 'switchoff1', 'switchoff2', 'switchoff3', 'switchoff4']
REQUESTS = [STATE, 'switch1', 'switch2', 'switch3', 'switch4']
INITIAL_VALUES = {
  '_state':  EVENT_ACTION_OFF,
  '_state1': EVENT_ACTION_OFF,
  '_state2': EVENT_ACTION_OFF,
  '_state3': EVENT_ACTION_OFF,
  '_state4': EVENT_ACTION_OFF
}


# https://aeotec.freshdesk.com/helpdesk/attachments/6009584527

def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_switch = Dsc11(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_switch.id] = new_switch
  return new_switch.id


class Dsc11(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    if self._node:
      self._switches = list(self._node.get_switches().keys())
    else:
      self._switches = None

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)
    self.add_command('switch1', self.switch1)
    self.add_command('switch2', self.switch2)
    self.add_command('switch3', self.switch3)
    self.add_command('switch4', self.switch4)
    self.add_command('switch1', self.switchoff1)
    self.add_command('switch2', self.switchoff2)
    self.add_command('switch3', self.switchoff3)
    self.add_command('switch4', self.switchoff4)

    self.add_request(STATE, self.get_state)
    self.add_request('switch1', self.get_state1)
    self.add_request('switch2', self.get_state2)
    self.add_request('switch3', self.get_state3)
    self.add_request('switch4', self.get_state4)

    self.add_action(STATE, metaSwitch())
    self.add_action('switch1', metaSwitch(on_action='switch1', off_action='switchoff1', title='Outlet 1', control_type='switch'))
    self.add_action('switch2', metaSwitch(on_action='switch2', off_action='switchoff2', title='Outlet 2', control_type='switch'))
    self.add_action('switch3', metaSwitch(on_action='switch3', off_action='switchoff3', title='Outlet 3', control_type='switch'))
    self.add_action('switch4', metaSwitch(on_action='switch4', off_action='switchoff4', title='Outlet 4', control_type='switch'))

    self._alexa_export = False
    #self.add_alexa_action(ALEXA_OFF)
    #self.add_alexa_action(ALEXA_ON)

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    For example when there is a gen6 multisensor I want it to always report every 5 minutes and timeout to be 30 
    seconds.
    Args:
      **kwargs ():
    """
    if self._update_try_count >= 5:
      self._config_updated = True
      return

    # TODO: self._sensitivity ??
    report = 2  # 1=hail 2=basic
    self.node.set_config_param(110, 1)
    self.node.set_config_param(100, 1)
    self.node.set_config_param(80, report)
    self.node.set_config_param(102, 15)
    self.node.set_config_param(111, 30)

    successful = True
    successful &= self.node.request_config_param(80) == report
    successful &= self.node.request_config_param(102) == 15

    self._update_try_count += 1
    self._config_updated = successful

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

    if self._switches is None:
      self._switches = list(self._node.get_switches().keys())

    self._state = EVENT_ACTION_ON if node.get_switch_state(self._switches[0]) else EVENT_ACTION_OFF
    self._state1 = EVENT_ACTION_ON if node.get_switch_state(self._switches[1]) else EVENT_ACTION_OFF
    self._state2 = EVENT_ACTION_ON if node.get_switch_state(self._switches[2]) else EVENT_ACTION_OFF
    self._state3 = EVENT_ACTION_ON if node.get_switch_state(self._switches[3]) else EVENT_ACTION_OFF
    self._state4 = EVENT_ACTION_ON if node.get_switch_state(self._switches[4]) else EVENT_ACTION_OFF

  def off(self, **kwargs):
    self._state = EVENT_ACTION_OFF
    self.setOff()
    return EVENT_ACTION_OFF

  def switchoff1(self, **kwargs):
    self.member_set('_state1', EVENT_ACTION_OFF)
    self.setOff(1)

  def switchoff2(self, **kwargs):
    self.member_set('_state2', EVENT_ACTION_OFF)
    self.setOff(2)

  def switchoff3(self, **kwargs):
    self.member_set('_state3', EVENT_ACTION_OFF)
    self.setOff(3)

  def switchoff4(self, **kwargs):
    self.member_set('_state4', EVENT_ACTION_OFF)
    self.setOff(4)

  def on(self, **kwargs):
    self._state = EVENT_ACTION_ON
    self.setOn()
    return EVENT_ACTION_ON

  def switch1(self, **kwargs):
    self.member_set('_state1', EVENT_ACTION_ON)
    self.setOn(1)

  def switch2(self, **kwargs):
    self.member_set('_state2', EVENT_ACTION_ON)
    self.setOn(2)

  def switch3(self, **kwargs):
    self.member_set('_state3', EVENT_ACTION_ON)
    self.setOn(3)

  def switch4(self, **kwargs):
    self.member_set('_state4', EVENT_ACTION_ON)
    self.setOn(4)

  def setOn(self, switch=0):
    self._node.set_switch(self._switches[switch], 1)

  def setOff(self, switch=0):
    self._node.set_switch(self._switches[switch], 0)

  def toggle(self, **kwargs):
    if self.state == EVENT_ACTION_ON:
      return self.off()
    return self.on()

  def get_state(self, **kwargs):
    return self.state

  def get_state1(self, **kwargs):
    return self._state1

  def get_state2(self, **kwargs):
    return self._state2

  def get_state3(self, **kwargs):
    return self._state3

  def get_state4(self, **kwargs):
    return self._state4

  @property
  def state(self):
    return self._state
