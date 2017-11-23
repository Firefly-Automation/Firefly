


TITLE = 'title'
CONTEXT = 'context'
REQUEST = 'request'
PARAM = 'key'
TEXT = 'text'
MAX_LENGTH = 'maxLength'
TYPE = 'type'
INDEX = 'displayIndex'

def settings_text(title, context, request, settings_param, index=100, max_length=25):
  settings = {
    TITLE: title,
    CONTEXT: context,
    REQUEST: request,
    PARAM: settings_param,
    TYPE: TEXT,
    MAX_LENGTH: max_length,
    INDEX: index
  }
  return settings

def settings_alias():
  return settings_text('Name', 'Set name of device', 'alias', 'alias', index=0)
