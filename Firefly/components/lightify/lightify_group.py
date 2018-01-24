from lightify import Group, Lightify

from Firefly import logging
from Firefly.components.lightify.lightify_device import LightifyDevice
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import ACTION_LEVEL, ACTION_OFF, ACTION_ON, ACTION_TOGGLE, COMMAND_UPDATE, DEVICE_TYPE_SWITCH, LEVEL, SWITCH
from Firefly.util.color import average_rgb

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
  lightify_group = LightifyGroup(firefly, package, **kwargs)
  firefly.install_component(lightify_group)
  return lightify_group.id


class LightifyGroup(LightifyDevice):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.lightify_type = 'GROUP'

  def update_lightify(self, lightify_object: Group = None, lightify_bridge: Lightify = None, **kwargs):
    logging.debug('[LIGHTIFY GROUP] : UPDATE LIGHTIFY')
    if lightify_object is None:
      return
    self.lightify_object: Group = lightify_object

    level = 0
    on = False

    r_values = []
    g_values = []
    b_values = []
    ct_avg = 0

    ct = 2700
    rgb = (0, 0, 0)

    for light in lightify_object.lights():
      light_object = lightify_bridge.lights()[light]
      on |= light_object.on()
      level += light_object.lum()

      ct_avg += light_object.temp()

      r_values.append(light_object.red())
      g_values.append(light_object.green())
      b_values.append(light_object.blue())

    if on:
      try:
        level = int(level / len(lightify_object.lights()))
        ct = int(ct_avg / len(lightify_object.lights()))
        rgb = average_rgb(r_values, g_values, b_values)
      except:
        level = 100
    else:
      level = 0

    self.update_values(level=level, switch=on, ct=ct, r=rgb[0], g=rgb[1], b=rgb[2])

    if self.lightify_object.name() != self._alias:
      self.set_alias(alias=self.lightify_object.name())
