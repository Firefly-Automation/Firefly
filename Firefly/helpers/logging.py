import logging

LOGGING_LEVEL = {
  'debug': logging.DEBUG,
  'info': logging.INFO,
  'warn': logging.WARNING,
  'error': logging.ERROR,
  'critical': logging.CRITICAL
}

class FireflyLogging(object):
  '''FireflyLogging waraps the default logging module.

  Using FireflyLogging allows logging messages to also go into the database be be used and displayed in the ui. This is
  a work in progress and only logs out to the screen now.
  '''
  def __init__(self, filename=None, level='debug'):
    if filename:
      logging.basicConfig(filename=filename)
    logging.basicConfig(level=LOGGING_LEVEL[level])

  def debug(self, message):
    logging.debug(message)

  def info(self, message):
    logging.info(message)

  def message(self, message):
    ''' message will also show up in the ui logs by defaults but logs as info'''
    logging.info(message)

  def warn(self, message):
    logging.warn(message)

  def error(self, message):
    logging.error(message)

  def critical(self, message):
    logging.critical(message)