from Firefly import logging
from Firefly.const import (IS_DARK, IS_LIGHT, IS_MODE, IS_NOT_MODE, IS_NOT_TIME_RANGE, IS_TIME_RANGE)


def check_conditions(firefly, condition: dict) -> bool:
  verify = True
  if not condition:
    return False

  for c, value in condition.items():
    if c == IS_DARK:
      verify &= check_is_dark(firefly, value)
    if c == IS_LIGHT:
      verify &= check_is_light(firefly, value)
    if c == IS_MODE:
      verify &= check_is_mode(firefly, value)
    if c == IS_NOT_MODE:
      verify &= check_is_not_mode(firefly, value)
    if c == IS_NOT_TIME_RANGE or c == IS_TIME_RANGE:
      # TODO: Checking time ranges should take a list of time ranges to check against. This will allow multiple time
      # ranges to be supported.
      logging.error('Time range checks not supported yet.')

  return verify


def check_is_dark(firefly, value):
  return firefly.location.isDark is value


def check_is_light(firefly, value):
  return firefly.location.isLight is value


def check_is_mode(firefly, modes):
  if type(modes) is not list:
    modes = [modes]
  return firefly.location.mode in modes


def check_is_not_mode(firefly, modes):
  if type(modes) is not list:
    modes = [modes]
  return firefly.location.mode not in modes