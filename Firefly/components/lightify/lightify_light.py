from lightify import Light

from Firefly import logging
from Firefly.components.lightify.lightify_device import LightifyDevice
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import ACTION_LEVEL, ACTION_OFF, ACTION_ON, ACTION_TOGGLE, DEVICE_TYPE_SWITCH, LEVEL, SWITCH

TITLE = 'Lightify Light'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ACTION_LEVEL]
REQUESTS = [SWITCH, LEVEL]


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  logging.message(str(kwargs))
  # TODO: Remove this in the future
  kwargs['tags'] = ['light']
  lightify_light = LightifyLight(firefly, package, **kwargs)
  firefly.install_component(lightify_light)


class LightifyLight(LightifyDevice):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.lightify_type = 'LIGHT'

  def update_lightify(self, lightify_object: Light = None, **kwargs):
    if lightify_object is None:
      return
    self.lightify_object: Light = lightify_object
    switch = ACTION_ON if self.lightify_object.on() else ACTION_OFF
    level = self.lightify_object.lum()

    self.update_values(level, switch)

    if self.lightify_object.name() != self._alias:
      self.set_alias(alias=self.lightify_object.name())
