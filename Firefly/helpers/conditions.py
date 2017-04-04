from Firefly import logging
from Firefly.const import (IS_DARK, IS_LIGHT, IS_MODE, IS_NOT_MODE, IS_NOT_TIME_RANGE, IS_TIME_RANGE)

class Conditions(object):
  def __init__(self, is_dark: bool=None, is_light: bool=None, is_mode: list=None, is_not_mode: list=None, last_mode: list=None, before_time=None, after_time=None, in_time_range=None, not_in_time_range=None):
    self.is_dark = is_dark
    self.is_light = is_light
    self.is_mode = is_mode
    self.is_not_mode = is_not_mode
    self.last_mode = last_mode
    self.before_time = before_time
    self.after_time = after_time
    self.in_time_range = in_time_range
    self.not_in_time_range = not_in_time_range


  def export(self):
    export_data = self.__dict__.copy()
    for item in self.__dict__:
      if export_data[item] is None:
        export_data.pop(item)
    return export_data


  def check_conditions(self, firefly) -> bool:
    valid = True
    if self.is_dark is not None:
      valid &= firefly.location.isDark is self.is_dark
    if self.is_light is not None:
      valid &= firefly.location.isLight is self.is_light
    if self.is_mode is not None:
      valid &= firefly.location.mode in self.is_mode
    if self.is_not_mode is not None:
      valid &= firefly.location.mode not in self.is_not_mode
    # TODO: Time based checks

    return valid