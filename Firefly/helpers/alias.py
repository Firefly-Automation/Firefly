from Firefly import logging
from Firefly.const import (ALIAS_FILE)
import json

class Alias(object):
  def __init__(self, alias_file=ALIAS_FILE):
    self._alias_file = alias_file
    self._aliases = {}

    self.read_file()

  def read_file(self):
    with open(self._alias_file) as file:
      self._aliases = json.load(file)

  def export_aliases(self):
    with open(self._alias_file, 'w') as file:
      json.dump(self.aliases, file, indent=4, sort_keys=True)

  def set_alias(self, device_id, alias) -> str:
    if alias in self.aliases.values():
      if device_id not in self.aliases or self.aliases[str(device_id)] != alias:
        try:
          alias_base = '-'.join(alias.split('-')[:-1])
          alias_number = int(alias.split('-')[-1])
        except:
          alias_number = 0
          alias_base = alias
          logging.error('Unknown error')
        alias_number += 1
        alias = str(alias_base + '-' + str(alias_number))
        return self.set_alias(device_id, alias)
    self.aliases[str(device_id)] = str(alias)
    return alias

  def get_alias(self, device_id):
    if device_id in self.aliases.keys():
      return self.aliases[device_id]

    return device_id

  def get_device_id(self, alias):
    if alias in self.aliases.values():
      print(self.aliases)
      device_id_list = [a for a in self.aliases if self.aliases[a] == alias]
      if len(device_id_list) != 1:
        logging.error(code='FF.ALI.GET.002', args=(alias))  # more than one ff_id matching alias: %s
        return None
      return device_id_list[0]
    if alias in self.aliases.keys():
      logging.debug('Seems like device_id was given, not alias')
      return alias
    logging.error(code='FF.ALI.GET.001', args=(alias))  # unknown error getting ff_id id for %s
    return None

  @property
  def aliases(self):
    return self._aliases

  @property
  def alias_list(self):
    return self._aliases.values()