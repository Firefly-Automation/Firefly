from Firefly import logging
from Firefly.helpers.conditions import Conditions
from Firefly.helpers.events import Command


class Action(object):
  def __init__(self, ff_id, command, source, conditions=None, force=False, **kwargs):
    self._ff_id = ff_id
    self._command = command
    self._source = source
    self._kwargs = kwargs
    self._force = force

    if type(conditions) is Conditions:
      self._conditions = conditions
    if type(conditions) is dict:
      self._conditions = Conditions(**conditions)


  def execute_action(self, firefly):
    if not self._force:
      if not self.conditions.check_conditions(firefly):
        return False
    command = Command(self.id, self.source, self.command, force=self._force, **self._kwargs)
    firefly.send_command(command)

  def export(self) -> dict:
    export_data = {
      'ff_id': self.id,
      'command': self.command,
      'force': self._force,
      'conditions': self.conditions.export(),
      'source': self.source
    }
    export_data.update(**self._kwargs)
    return export_data

  @property
  def id(self):
    return self._ff_id

  @property
  def command(self):
    return self._command

  @property
  def source(self):
    return self._source

  @property
  def conditions(self):
    return self._conditions