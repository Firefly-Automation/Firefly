from optparse import OptionParser, IndentedHelpFormatter
from configparser import ConfigParser
import json

DESC = '''error_code_util is used to add and modify project error codes.\n
The error code format will be: FF.DEV.EXP.001
FF -> Project code ]
DEV [file_code] -> First letters in file where error is. (device.py)
EXP [func_code] -> First three letters in function name where error is. (export)
001 -> Number of error in function. This will start at 001 and if a gap is created due to a deleted error code it 
will backfill.'''


class Formatter(IndentedHelpFormatter):
  """Custom help formatter that does not reformat the description."""

  def format_description(self, description):
    return description + "\n"


class ErrorCode(object):
  def __init__(self, error_entry={}):
    self._error_entry = error_entry
    self._error_code = ''
    self._project_code = ''
    self._file_code = ''
    self._function_code = ''
    self._error_num = ''
    self._message = error_entry.get('error_message', '')
    self._file_name = error_entry.get('file_name', '')
    self._function_name = error_entry.get('function_name', '')
    if error_entry:
      self.parse_error_code()

  def parse_error_code(self):
    self._error_code = self._error_entry['error_code']
    code = self.error_code.split('.')
    self._project_code = code[0]
    self._file_code = code[1]
    self._function_code = code[2]
    self._error_num = code[3]

  def __str__(self):
    return f'{self.message} ({self.file_name} - {self.function_name})'

  @property
  def error_code(self):
    return self._error_code

  @property
  def project_code(self):
    return self._project_code

  @property
  def file_code(self):
    return self._file_code

  @property
  def function_code(self):
    return self._function_code

  @property
  def error_num(self):
    return int(self._error_num)

  @property
  def message(self):
    return self._message

  @property
  def file_name(self):
    return self._file_name

  @property
  def function_name(self):
    return self._function_name

  @property
  def dict(self):
    return {
      'error_code':    self.error_code,
      'error_message': self.message,
      'project_code':  self.project_code,
      'file_name':     self.file_name,
      'function_name': self.function_name
    }


class ErrorCodes(object):
  def __init__(self, error_code_file='error_cods.json'):
    self.error_code_file = error_code_file
    self.error_codes = []
    self.read()

  def read(self):
    with open(self.error_code_file) as error_file:
      error_data = json.load(error_file)
    error_codes = []
    for d in error_data.values():
      error_codes.append(ErrorCode(d))
    self.error_codes = error_codes

  def write(self):
    error_code_dict = {}
    for ec in self.error_codes:
      error_code_dict[ec.error_code] = ec.dict
    with open(self.error_code_file, 'w') as error_file:
      json.dump(error_code_dict, error_file, indent=4, sort_keys=True)

  def delete_error(self, error_code):
    new_errors = [x for x in self.error_codes if x.error_code != error_code.upper()]
    self.error_codes = new_errors
    self.write()

  def get(self, error_code):
    try:
      error = [x for x in self.error_codes if x.error_code == error_code]
      return error[0]
    except IndexError:
      raise ValueError

  def get_error_number(self, project_code, file_code, function_code):
    error_codes_scope = [x.error_num for x in self.error_codes if
      x.project_code == project_code and x.file_code == file_code and x.function_code == function_code]
    error_codes_scope.sort()
    for error_number in range(len(error_codes_scope)):
      try:
        if error_number + 1 != error_codes_scope[error_number]:
          return error_number + 1
      except:
        pass
    return len(error_codes_scope) + 1

  def create_error_code(self, project_code, file_name, function_name):
    file_code = file_name[:3].upper()
    func_code = function_name[:3].upper()
    error_number = self.get_error_number(project_code, file_code, func_code)

    return f'{project_code}.{file_code}.{func_code}.{"%03d" % error_number}'.upper()

  def create_message(self, error_code, message):
    return (f'[{error_code}] {message.lower()}')

  def create_error_entry(self, project_code, file_name, function_name, error_message):
    error_code = self.create_error_code(project_code, file_name, function_name)
    message = self.create_message(error_code, error_message)

    error_entry = ErrorCode({
      'error_code':    error_code,
      'error_message': message,
      'project_code':  project_code,
      'file_name':     file_name,
      'function_name': function_name
    })
    self.error_codes.append(error_entry)
    self.write()
    return error_entry


def update_config(options):
  config = ConfigParser()
  config.read('error_code_util.config')
  config.set('ERROR_CODE_CONFIG', 'project_code', options.project)
  config.set('ERROR_CODE_CONFIG', 'file', options.error_file)
  with open('error_code_util.config', 'w') as configfile:
    config.write(configfile)


if __name__ == '__main__':
  parser = OptionParser(usage="usage: %prog [options] file_code func_code error_message", formatter=Formatter(),
                        description=DESC)
  parser.add_option('-f', '--file', dest='error_file', default='error_codes.json', type='string',
                    help='specify error code json file.')
  parser.add_option('-p', '--project', dest='project', default='FF', type='string', help='Project code in error code')
  parser.add_option('-s', '--save_settings', dest='save_settings', action="store_true",
                    help='Save settings to settings files.', default=False)
  parser.add_option('-d', '--delete', dest='delete_error', type='string', help='Delete error code.')
  parser.add_option('-g', '--get', dest='get_error', type='string', help='Get error code')

  (options, args) = parser.parse_args()

  if options.save_settings:
    update_config(options)
    exit()

  config = ConfigParser()
  config.read('error_code_util.config')
  project_code = config.get('ERROR_CODE_CONFIG', 'project_code', fallback=options.project)
  error_file = config.get('ERROR_CODE_CONFIG', 'file', fallback=options.error_file)
  error_codes = ErrorCodes(error_file)

  if options.delete_error:
    error_codes.delete_error(options.delete_error)
    exit()

  if options.get_error:
    try:
      print(f'\n{error_codes.get(options.get_error)}\n')
    except ValueError:
      print('\nError getting error code.\n')
    exit()

  if len(args) < 3:
    parser.error('Not enough inputs')

  if len(args) > 3:
    args[2] = ' '.join(args[2:])

  file_name = args[0]
  function_name = args[1]
  error_message = args[2]

  entry = error_codes.create_error_entry(project_code, file_name, function_name, error_message)

  python_code = f'logging.error(code=\'{entry.error_code}\')'

  print(f'\n{entry}')
  print("\nPut this where you want your error to be called:")
  print(python_code)
  print('\n')
