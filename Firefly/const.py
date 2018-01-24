from typing import TypeVar

EVENT_ACTON_TYPE = TypeVar('EVENT_ACTION', dict, str, list)

AUTHOR = 'Zachary Priddy (me@zpriddy.com)'
VERSION = '0.0.0.c'

# #### SETTINGS ####
FIREFLY_CONFIG_SECTION = 'FIREFLY'
CONFIG_PORT = 'port'
CONFIG_DEFAULT_PORT = 6002
CONFIG_HOST = 'host'
CONFIG_DEFAULT_HOST = 'localhost'
CONFIG_MODES = 'modes'
CONFIG_MODES_DEFAULT = 'home, away, morning, night'
CONFIG_POSTAL_CODE = 'postal_code'
CONFIG_BEACON = 'beacon'
CONFIG_FILE = 'dev_config/firefly.config'

SERVICE_CONFIG_FILE = 'dev_config/services.config'
NEST_CACHE_FILE = 'dev_config/service_nest_cache.config'

ALIAS_FILE = 'dev_config/device_alias.json'
DEVICE_FILE = 'dev_config/devices.json'
AUTOMATION_FILE = 'dev_config/automation.json'
LOCATION_FILE = 'dev_config/location.json'
ZWAVE_FILE = 'dev_config/zwave.json'
GROUPS_CONFIG_FILE = 'dev_config/groups.json'
ROUTINES_CONFIG_FILE = 'dev_config/routines.json'
SECURITY_SETTINGS_FILE = 'dev_config/security_settings.json'

REQUIRED_FILES = {
  ALIAS_FILE:             {},
  AUTOMATION_FILE:        [],
  ROUTINES_CONFIG_FILE:   [],
  CONFIG_FILE:            None,
  DEVICE_FILE:            [],
  GROUPS_CONFIG_FILE:     {},
  LOCATION_FILE:          {},
  SERVICE_CONFIG_FILE:    None,
  SECURITY_SETTINGS_FILE: {}
}

# FOOBOT SERVICE
SERVICE_FOOBOT = 'service_foobot'
FOOBOT_SECTION = 'FOOBOT'

TYPE_ZWAVE_SERVICE = 'zwave_service'

SERVICE_NOTIFICATION = 'FIREFLY_NOTIFICATION_SERVICE'
NOTIFY_DEFAULT = 'DEFAULT'
PRIORITY_NORMAL = 0
PRIORITY_LOW = -1
PRIORITY_HIGH = 1
PRIORITY_EMERGENCY = 2

# #### EVENT TYPES ####
EVENT_TYPE_ANY = 'ANY'
EVENT_TYPE_COMMAND = 'COMMAND'
EVENT_TYPE_UPDATE = 'UPDATE'
EVENT_TYPE_BROADCAST = 'BROADCAST'
EVENT_TYPE_REQUEST = 'REQUEST'

# #### EVENT ACTIONS ####
EVENT_ACTION_ANY = 'ANY'
EVENT_ACTION_ON = 'on'
EVENT_ACTION_OFF = 'off'
EVENT_ACTION_ACTIVE = 'active'
EVENT_ACTION_INACTIVE = 'inactive'
EVENT_ACTION_OPEN = 'open'
EVENT_ACTION_CLOSE = 'close'
EVENT_ACTION_LEVEL = 'level'
EVENT_ACTION_MODE = 'mode'

EVENT_PROPERTY_ANY = 'ANY'

TYPE_AUTOMATION = 'TYPE_AUTOMATION'
TYPE_ROUTINE = 'TYPE_ROUTINE'
TYPE_DEVICE = 'TYPE_DEVICE'
TYPE_SERVICE = 'TYPE_SERVICE'
TYPE_LOCATION = 'TYPE_LOCATION'

API_INFO_REQUEST = 'API_INFO_REQUEST'
API_FIREBASE_VIEW = 'API_FIREBASE_VIEW'
API_ALEXA_VIEW = 'API_ALEXA_VIEW'

EVENT_DAWN = 'dawn'
EVENT_SUNRISE = 'sunrise'
EVENT_NOON = 'noon'
EVENT_SUNSET = 'sunset'
EVENT_DUSK = 'dusk'
DAY_EVENTS = [EVENT_DAWN, EVENT_SUNRISE, EVENT_NOON, EVENT_SUNSET, EVENT_DUSK]

# #### COMMAND ACTIONS ####
COMMAND_NOTIFY = 'NOTIFY'
COMMAND_SPEECH = 'SPEECH'
COMMAND_ROUTINE = 'ROUTINE'
COMMAND_SET_LIGHT = 'set_light'

FIREFLY_SECURITY_MONITORING = 'security_and_monitoring_service'

ACTION_OFF = 'off'
ACTION_ON = 'on'
ACTION_TOGGLE = 'toggle'
ACTION_LEVEL = 'level'
ACTION_SET_PRESENCE = 'set_presence'
ACTION_PRESENT = 'present'
ACTION_NOT_PRESENT = 'not_present'

# #### PRESENCE WITH BEACON ####
ACTION_PRESENT_BEACON = 'BEACON_PRESENT'
ACTION_NOT_PRESENT_BEACON = 'BEACON_NOT_PRESENT'
ACTION_ENABLE_BEACON = 'BEACON_ENABLE'
ACTION_SET_DELAY = 'SET_DELAY'

# #### REQUESTS ####
STATE = 'state'
LEVEL = 'level'
SWITCH = 'switch'
CONTACT = 'contact'
PRESENCE = 'presence'
MOTION = 'motion'
LUX = 'lux'
BEACON_ENABLED = 'BECAON_ENABLED'
TEMPERATURE = 'temperature'

NOT_ENABLED = False
ENABLED = True

STATE_CLOSED = 'close'
STATE_OPEN = 'open'

# ### TAG VALUES ###
SWITCH_OFF = EVENT_ACTION_OFF
SWITCH_ON = EVENT_ACTION_ON

CONTACT_CLOSED = STATE_CLOSED
CONTACT_OPEN = STATE_OPEN

MOTION_ACTIVE = EVENT_ACTION_ACTIVE
MOTION_INACTIVE = EVENT_ACTION_INACTIVE

# ### PRESENCE ####
PRESENT = 'present'
NOT_PRESENT = 'not_present'

# #### DEVICE TYPES ####
DEVICE_TYPE_SWITCH = 'switch'
DEVICE_TYPE_DIMMER = 'dimmer'
DEVICE_TYPE_COLOR_LIGHT = 'COLOR_LIGHT'
DEVICE_TYPE_THERMOSTAT = 'THERMOSTAT'
DEVICE_TYPE_NOTIFICATION = 'NOTIFICATION'
DEVICE_TYPE_MOTION = 'MOTION'
DEVICE_TYPE_PRESENCE = 'presence'
DEVICE_TYPE_CONTACT = 'contact'

SOURCE_LOCATION = 'location'
SOURCE_TIME = 'time'

SOURCE_TRIGGER = 'SOURCE_TRIGGER'

COMMAND_UPDATE = 'UPDATE'

TIME = 'time'

# #### CONDITIONS ####
IS_DARK = 'IS_DARK'
IS_LIGHT = 'IS_LIGHT'
IS_MODE = 'IS_MODE'
IS_NOT_MODE = 'IS_NOT_MODE'
IS_TIME_RANGE = 'TIME_RANGE'
IS_NOT_TIME_RANGE = 'NOT_TIME_RANGE'

COMPONENT_MAP = [{
  'type': TYPE_AUTOMATION,
  'file': AUTOMATION_FILE
}, {
  'type': TYPE_DEVICE,
  'file': DEVICE_FILE
}, {
  'type': TYPE_ROUTINE,
  'file': ROUTINES_CONFIG_FILE
}]

# TODO: This may not be needed
SENSORS = {
  'Energy':            'ENERGY',
  'Previous Reading':  'PREVIOUS READING',
  'Interval':          'INTERVAL',
  'Power':             'POWER',
  'Voltage':           'VOLTAGE',
  'Current':           'CURRENT',
  'Exporting':         'EXPORTING',
  'Sensor':            'SENSOR',
  'Temperature':       'TEMPERATURE',
  'Luminance':         'LUMINANCE',
  'Relative Humidity': 'RELATIVE HUMIDITY',
  'Ultraviolet':       'ULTRAVIOLET'
}

# ALEXA
ALEXA_DEC_PERCENTAGE = "decrementPercentage"
ALEXA_DEC_COLOR_TEMP = "decrementColorTemperature"
ALEXA_DEC_TARGET_TEMP = "decrementTargetTemperature"
ALEXA_GET_LOCK = "getLockState"
ALEXA_GET_COLOR_TEMP = "getTargetTemperature"
ALEXA_GET_TEMP = "getTemperatureReading"
ALEXA_INC_PERCENTAGE = "incrementPercentage"
ALEXA_INC_COLOR_TEMP = "incrementColorTemperature"
ALEXA_INC_TEMP = "incrementTargetTemperature"
ALEXA_SET_COLOR = "setColor"
ALEXA_SET_COLOR_TEMP = "setColorTemperature"
ALEXA_SET_LOCK = "setLockState"
ALEXA_SET_PERCENTAGE = "setPercentage"
ALEXA_SET_TEMP = "setTargetTemperature"
ALEXA_ON = "turnOff"
ALEXA_OFF = "turnOn"

ALEXA_SET_PERCENTAGE_REQUEST = 'SetPercentageRequest'
ALEXA_ON_REQUEST = 'TurnOnRequest'
ALEXA_OFF_REQUEST = 'TurnOffRequest'
ALEXA_SET_COLOR_TEMP_REQUEST = 'SetColorTemperatureRequest'
ALEXA_SET_COLOR_REQUEST = 'SetColorRequest'

# WATER SENSOR
WATER = 'water'
SENSOR_DRY = 'dry'
SENSOR_WET = 'wet'
DEVICE_TYPE_WATER_SENSOR = 'water_sensor'
