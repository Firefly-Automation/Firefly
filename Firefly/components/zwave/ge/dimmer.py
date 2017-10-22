from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue

from Firefly import logging
from Firefly.components.zwave.device_types.switch import ZwaveSwitch
from Firefly.const import ACTION_OFF, ACTION_ON, COMMAND_SET_LIGHT, DEVICE_TYPE_DIMMER, EVENT_ACTION_OFF, LEVEL, STATE, SWITCH
from Firefly.helpers.metadata import metaDimmer

TITLE = 'Firefly GE Dimmer'
DEVICE_TYPE = DEVICE_TYPE_DIMMER
AUTHOR = 'Zachary Priddy'

INITIAL_VALUES = {
  '_state':     EVENT_ACTION_OFF,
  '_level':     0,
  '_min_level': 5
}

COMMANDS = [ACTION_OFF, ACTION_ON, LEVEL, COMMAND_SET_LIGHT]

REQUESTS = [SWITCH, LEVEL, STATE]

CAPABILITIES = {
  LEVEL:  True,
  SWITCH: True,
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  dimmer = GEDimmer(firefly, package, **kwargs)
  firefly.install_component(dimmer)
  return dimmer.id


class GEDimmer(ZwaveSwitch):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs.update({
      'initial_values': INITIAL_VALUES,
      'commands':       COMMANDS,
      'requests':       REQUESTS
    })
    super().__init__(firefly, package, TITLE, capabilities=CAPABILITIES, **kwargs)

    self.add_command(COMMAND_SET_LIGHT, self.set_light)
    self.add_action('LEVEL_OLD', metaDimmer())

  def set_light(self, **kwargs):
    self.set_level(**kwargs)

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    old_level = self.get_level()
    super().update_from_zwave(node, ignore_update, values, values_only, **kwargs)

    if self.value_map.get('Level') is None:
      return
    # Check if level is less than min_level, set light to min level
    dimmer_id = self.value_map['Level']
    level = node.get_dimmer_level(dimmer_id)
    if level == old_level and 0 < level < self._min_level:
      logging.debug('SETTING GE DIMMER LEVEL')
      self.set_level(level=self._min_level)
