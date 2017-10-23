'''
package_lookup contains tools to lookup packages for new zwave devices. This includes workarounds for devices not in openzwave
'''

from openzwave.network import ZWaveNode

from Firefly import logging

PACKAGE = 'package'
ALIAS = 'alias'
MODULE = 'module'
PACKAGE_BASE = 'Firefly.components.zwave'

# Workaround mapping uses the product name to define unknown devices.
WORK_AROUND_MAPPING = {
  # Leviton DZS15 Zwave Switch
  'unknown:_type=1c02,_id=0334': {
    PACKAGE: 'leviton.dzs15',
    ALIAS:   'Levition Zwave Switch'
  },  # Ecolink Door Window Plus Sensor
  'unknown:_type=0004,_id=0002': {
    PACKAGE: 'ecolink.contact_sensor',
    ALIAS:   'Ecolink Door/Window'
  },
  'zw080_siren_gen5':            {
    PACKAGE: 'zwave_aeotec_zw080',
    ALIAS:   'ZW080 Siren'
  }
}

AVAILABLE_PACKAGES = {
  'aeotec': ['dsc06106_smart_energy_switch', 'zw096_smart_switch_6', 'zw100_multisensor_6', 'zw100_multisensor_6', 'zw120_door_window_sensor_gen5', 'zw112_door_window_sensor_6', 'dsb45_water_sensor']
}

LINKED_PACKAGES = {
  'ge': {
    '14294_in-wall_smart_dimmer':  {
      PACKAGE: 'ge.dimmer',
      ALIAS:   'GE Dimmer'
    },
    '12724_3-way_dimmer-Switch':   {
      PACKAGE: 'ge.dimmer',
      ALIAS:   'GE Dimmer'
    },
    '12729_3-way_dimmer-Switch':   {
      PACKAGE: 'ge.dimmer',
      ALIAS:   'GE Dimmer'
    },
    'unknown:_type=4953,_id=3133': {
      PACKAGE: 'zwave_generic_devices.motion_sensor',
      ALIAS:   'GE ZW6302 Motion Sensor'
    }
  }
}

DEVICE_TYPE_MAPPING = {
  'on/off relay switch':  'zwave_generic_devices.switch',
  'on/off power switch':  'zwave_generic_devices.switch',
  'door/window sensor':   'zwave_generic_devices.contact_sensor',
  'door/window detector': 'zwave_generic_devices.contact_sensor',
  'motion sensor':        'zwave_generic_devices.motion_sensor',
  'motion detector':      'zwave_generic_devices.motion_sensor'
}


def get_package(node: ZWaveNode) -> dict:
  ''' Gets the zwave package and device alias based off of the type of device, malefactor, and workaround.

  Args:
    node: zwave node object

  Returns: dict (module, alias) The module and alias for the zwave device
  '''
  product_name = node.product_name.lower().replace(' ', '_')
  product_type = node.product_type.lower()
  manufacturer_name = node.manufacturer_name.lower().replace(' ', '_')
  product_id = node.product_id.lower()
  device_type = node.device_type.lower()

  if manufacturer_name in AVAILABLE_PACKAGES:
    if product_name in AVAILABLE_PACKAGES[manufacturer_name]:
      return {
        MODULE: '%s.%s.%s' % (PACKAGE_BASE, manufacturer_name, product_name),
        ALIAS:  node.product_name,
        'node': node
      }

  if manufacturer_name in LINKED_PACKAGES:
    if product_name in LINKED_PACKAGES[manufacturer_name]:
      package_info = LINKED_PACKAGES[manufacturer_name][product_name]
      return {
        MODULE:            '%s.%s' % (PACKAGE_BASE, package_info[PACKAGE]),
        ALIAS: package_info[ALIAS],
        'node':            node
      }

  if product_name in WORK_AROUND_MAPPING:
    package_info = WORK_AROUND_MAPPING[product_name]
    return {
      MODULE:            '%s.%s' % (PACKAGE_BASE, package_info[PACKAGE]),
      ALIAS: package_info[ALIAS],
      'node':            node
    }

  if not node.is_ready:
    logging.message('Node is not ready, Waiting for more info.')
    return {}

  # Generic device types
  product_name = node.product_name.lower()
  if product_name in DEVICE_TYPE_MAPPING:
    return {
      MODULE: '%s.%s' % (PACKAGE_BASE, DEVICE_TYPE_MAPPING[product_name]),
      ALIAS:  node.product_name
    }

  print('******************************************')
  print(node.node_id)
  print(node.product_name)
  print(node.product_type)
  print(node.product_id)
  print(node.product_type)
  print(node.manufacturer_id)
  print(node.manufacturer_name)
  print(node.command_classes_as_string)
  print(node.command_classes)
  print(node.is_ready)
  print(node.to_dict())
  print('******************************************')

  return {}
