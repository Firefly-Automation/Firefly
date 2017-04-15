import logging
import inspect
import os
import asyncio


from Firefly.const import COMMAND_NOTIFY, SERVICE_NOTIFICATION

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
    logging.basicConfig(level=LOGGING_LEVEL[level], format='%(asctime)s\t%(levelname)s:\t%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

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
    logging.info('%-130s [%s - %s]' % (message, function_name, file_name))

    if self.firefly is None:
      return
    from Firefly.helpers.events import Command
    notify = Command(SERVICE_NOTIFICATION,'LOGGING', COMMAND_NOTIFY, message=message)
    # TODO: Uncomment when you want notifications
    s = self.firefly.send_command(notify)


  def debug(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.debug('%-130s [%s - %s]' % (message, function_name, file_name))

  def info(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.info('%-130s [%s - %s]' % (message, function_name, file_name))

  def message(self, message):
    ''' message will also show up in the ui logs by defaults but logs as info'''
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.info('%-130s [%s - %s]' % (message, function_name, file_name))

  def warn(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.warning('%-130s [%s - %s]' % (message, function_name, file_name))

  def error(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.error('%-130s [%s - %s]' % (message, function_name, file_name))

  def critical(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.critical('%-130s [%s - %s]' % (message, function_name, file_name))