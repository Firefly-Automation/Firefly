
TYPE_TEXT = 'text'
TYPE_CHIP_LIST = 'chipList'
OPTIONS = 'options'
CONTEXT = 'context'
TITLE = 'title'
PARAM = 'param'
MAX_LENGTH = 'maxLength'
TYPE = 'type'
INDEX = 'displayIndex'


def settings_text(title='', context='', param='', max_length=20, display_index=100):
  return {
    TITLE:      title,
    CONTEXT:    context,
    PARAM:      param,
    MAX_LENGTH: max_length,
    TYPE:       TYPE_TEXT,
    INDEX:      display_index
  }


def settings_alias():
  return settings_text('Name', 'Set device name', 'alias')


def settings_chip_list(title='', context='', param='', options=[], display_index=100):
  return {
    TITLE:   title,
    CONTEXT: context,
    PARAM:   param,
    OPTIONS: options,
    TYPE:    TYPE_CHIP_LIST,
    INDEX:   display_index
  }


def settings_device_tags(options=['light', 'switch', 'outet', 'fan', 'contact', 'motion', 'lux', 'temperature', 'humidity', 'door', 'window', 'lamp', 'dimmer']):
  return settings_chip_list(title='Tags', context='Set device tags to enable better automation. Tags represent the device type. i.e. Light or Door', param='tags', options=options, display_index=0)