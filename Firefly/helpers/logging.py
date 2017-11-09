import inspect
import logging
import os

from Firefly import error_codes
from Firefly.const import COMMAND_NOTIFY, SERVICE_NOTIFICATION

from logging.handlers import RotatingFileHandler

LOG_PATH = '/opt/firefly_system/logs/new_firefly_log.log'
FORMAT = '%(asctime)s\t%(levelname)s:\t%(message)s'

LOGGING_LEVEL = {
  'debug':    logging.DEBUG,
  'info':     logging.INFO,
  'warn':     logging.WARNING,
  'error':    logging.ERROR,
  'critical': logging.CRITICAL
}


class FireflyLogging(object):
  '''FireflyLogging waraps the default logging module.

  Using FireflyLogging allows logging messages to also go into the database be be used and displayed in the ui. This is
  a work in progress and only logs out to the screen now.
  '''

  def __init__(self, filename=None, level='debug'):
    self.firefly = None
    if filename:
      logging.basicConfig(filename=filename)
    logging.basicConfig(level=LOGGING_LEVEL[level], format='%(asctime)s\t%(levelname)s:\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    self.logger = logging.getLogger('Firefly Logger')
    self.logger.setLevel(LOGGING_LEVEL[level])
    try:
      handler = RotatingFileHandler(LOG_PATH, maxBytes=100000000, backupCount=5)
      fmt = logging.Formatter(FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
      handler.setFormatter(fmt)
      self.logger.addHandler(handler)
    except:
      logging.error('Error setting up logger')

  def Startup(self, firefly):
    """
    Startup adds the firefly object. This allows us to use the notification service.

    Run this after firefly is initialized.
    Args:
      firefly (firefly): Firefly object
    """
    self.firefly = firefly

  def notify(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    self.logger.info('%-130s [%s - %s]' % (message, function_name, file_name))

    if self.firefly is None:
      return
    from Firefly.helpers.events import Command
    notify = Command(SERVICE_NOTIFICATION, 'LOGGING', COMMAND_NOTIFY, message=message)
    self.firefly.send_command(notify)

  def debug(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    self.logger.debug('%-130s [%s - %s]' % (message, function_name, file_name))

  def info(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    self.logger.info('%-130s [%s - %s]' % (message, function_name, file_name))

  def message(self, message):
    ''' message will also show up in the ui logs by defaults but logs as info'''
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    self.logger.info('%-130s [%s - %s]' % (message, function_name, file_name))

  def warn(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    self.logger.warning('%-130s [%s - %s]' % (message, function_name, file_name))

  def error(self, message='', code: str = None, args: tuple = None):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    try:
      if code:
        if args:
          message = str(error_codes.get(code)) % args
        else:
          message = error_codes.get(code)
        self.logger.error('%-130s [%s - %s]' % (message, function_name, file_name))
    except:
      self.logger.error('error getting code: %-130s [%s - %s]' % (code, function_name, file_name))
      # TODO: Log errors to Fierbase for future debugging

  def critical(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    self.logger.critical('%-130s [%s - %s]' % (message, function_name, file_name))
