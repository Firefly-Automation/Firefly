from Firefly import logging
from Firefly.components.lightify.lightify_device import LightifyDevice
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import ACTION_LEVEL, ACTION_OFF, ACTION_ON, ACTION_TOGGLE, DEVICE_TYPE_SWITCH, LEVEL, STATE, SWITCH, COMMAND_UPDATE
from lightify import Group, Lightify

TITLE = 'Lightify Group'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ACTION_LEVEL, COMMAND_UPDATE]
REQUESTS = [SWITCH, LEVEL]


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  logging.message(str(kwargs))
  # TODO: Remove this in the future
  kwargs['tags'] = ['light']
  lightify_light = LightifyGroup(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[lightify_light.id] = lightify_light


class LightifyGroup(LightifyDevice):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.lightify_type = 'GROUP'


  def update_lightify(self, lightify_object:Group = None, lightify_bridge:Lightify = None, **kwargs):
    logging.debug('[LIGHTIFY GROUP] : UPDATE LIGHTIFY')
    if lightify_object is None:
      return
    self.lightify_object: Group = lightify_object

    level = 0
    on = False

    for light in lightify_object.lights():
      light_object = lightify_bridge.lights()[light]
      on |= light_object.on()
      level += light_object.lum()

    if on:
      try:
        level = int(level / len(lightify_object.lights()))
      except:
        level = 100
    else:
      level = 0

    self.update_values(level=level, switch=on)

    if self.lightify_object.name() != self._alias:
      self.set_alias(alias=self.lightify_object.name())
