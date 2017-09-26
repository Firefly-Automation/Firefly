from Firefly import logging
from Firefly.helpers.conditions import Conditions
from Firefly.helpers.events import Command
from Firefly import scheduler


class Action(object):
  def __init__(self, ff_id, command, source, conditions=None, force=False, **kwargs):
    self._ff_id = ff_id
    self._command = command
    self._source = source
    self._kwargs = kwargs
    self._force = force
    self._delay_s = kwargs.get('delay_s')
    self._delay_m = kwargs.get('delay_m')
    self._conditions = None

    if type(conditions) is Conditions:
      self._conditions = conditions
    if type(conditions) is dict:
      self._conditions = Conditions(**conditions)


  def execute_action(self, firefly):
    if self._delay_s:
      scheduler.runInS(self._delay_s,self.execute,firefly=firefly)
    elif self._delay_m:
      scheduler.runInM(self._delay_m,self.execute,firefly=firefly)
    else:
      self.execute(firefly)


  def execute(self, firefly):
    if self._force or self.conditions is None:
      command = Command(self.id, self.source, self.command, force=self._force, **self._kwargs)
      firefly.send_command(command)
      return True

    if self.conditions.check_conditions(firefly):
      command = Command(self.id, self.source, self.command, force=self._force, **self._kwargs)
      firefly.send_command(command)
      return True
    return False

  def export(self) -> dict:
    export_data = {
      'ff_id': self.id,
      'command': self.command,
      'force': self._force,
      'source': self.source
    }
    if self.conditions:
      export_data['conditions'] = self.conditions.export()
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