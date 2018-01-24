from Firefly.helpers.events import Command

def command_from_dict(ff_id:str, source:str, command_dict:dict) -> Command:
  """ Create command from dict

  Args:
    ff_id: ff id of device to send command to
    source: source sending command
    command_dict: dict of command

  Returns: (Command) the command object

  """
  if type(command_dict) is not dict:
    return None
  command_str = list(command_dict.keys())[0]
  command_args = command_dict[command_str]
  return Command(ff_id, source, command_str, **command_args)