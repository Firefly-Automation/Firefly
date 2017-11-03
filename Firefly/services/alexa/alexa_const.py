ALEXA_VERSION_NUMBER = 1
STOP_INTENT = 'AMAZON.StopIntent'
CANCEL_INTENT = 'AMAZON.CancelIntent'
HELP_INTENT = 'AMAZON.HelpIntent'
TYPE_LAUNCH = 'LaunchRequest'

ALEXA_DISCOVERY = 'DiscoverAppliancesRequest'
ALEXA_DISCOVERY_NAMESPACE = 'Alexa.ConnectedHome.Discovery'
ALEXA_CONTROL_NAMESPACE = 'Alexa.ConnectedHome.Control'

STATE = 'state'
DEVICE = 'device'
LEVEL = 'level'
MODE = 'mode'

SWITCH_INTENT = 'Switch'
DIMMER_INTENT = 'Dimmer'
MODE_INTENT = 'ChangeMode'

SUPPORTED_INTENTS = {
  SWITCH_INTENT: {
    'required': [STATE, DEVICE]
  },
  DIMMER_INTENT: {
    'required': [LEVEL, DEVICE]
  },
  MODE_INTENT:   {
    'required': [MODE]
  }
}


def make_response(output_speech, card_content, output_type="PlainText", card_title="Firefly Smart Home",
                  card_type="Simple", end_session=True):
  response = {
    "version":  ALEXA_VERSION_NUMBER,
    "response": {
      "outputSpeech":     {
        "type": output_type,
        "text": output_speech
      },
      "card":             {
        "type":    card_type,
        "title":   card_title,
        "content": card_content
      },
      'shouldEndSession': end_session
    }
  }
  return response


STOP_RESPONSE = make_response('', 'Request Canceled')
HELP_RESPONSE = make_response(
    'With this skill you can control your firefly system. For example you can say, Alexa, tell firefly to turn off '
    'kitchen lights. What would you like me to do right now?',
    'With this skill you can control your firefly system. For example you can say, Alexa, tell firefly home to turn '
    'off kitchen lights. What would you like me to do right now?', end_session=False)
WELCOME_RESPONSE = make_response(
    'Welcome to Firefly. With this skill you can control your firefly system. For example you can say, Alexa, '
    'tell firefly to turn off kitchen lights. What would you like me to do right now?',
    'Welcome to Firefly. With this skill you can control your firefly system. For example you can say, Alexa, '
    'tell firefly home to turn off kitchen lights. What would you like me to do right now?', end_session=False)

UNSUPPORTED_COMMAND = make_response('The requested command is unsupported', 'The requested command is unsupported')

REQUEST_SLOT_FILLING = {
  "version":           ALEXA_VERSION_NUMBER,
  "response":          {
    "directives":       [{
      "type": "Dialog.Delegate"
    }],
    "shouldEndSession": False
  },
  "sessionAttributes": {}
}

## ALEXA SMART HOME CONST
ALEXA_INTERFACE = {
  "type":      "AlexaInterface",
  "interface": "Alexa",
  "version":   "3"
}

ALEXA_COLOR_TEMPERATURE_INTERFACE = {
  "type":       "AlexaInterface",
  "interface":  "Alexa.ColorTemperatureController",
  "version":    "3",
  "properties": {
    "supported":           [
      {
        "name": "colorTemperatureInKelvin"
      }
    ],
    "proactivelyReported": False,
    "retrievable":         True
  }
}

ALEXA_COLOR_INTERFACE = {
  "type":       "AlexaInterface",
  "interface":  "Alexa.ColorController",
  "version":    "3",
  "properties": {
    "supported":           [
      {
        "name": "color"
      }
    ],
    "proactivelyReported": False,
    "retrievable":         True
  }
}

ALEXA_BRIGHTNESS_INTERFACE = {
  "type":       "AlexaInterface",
  "interface":  "Alexa.BrightnessController",
  "version":    "3",
  "properties": {
    "supported":           [
      {
        "name": "brightness"
      }
    ],
    "proactivelyReported": False,
    "retrievable":         True
  }
}

ALEXA_POWER_INTERFACE = {
  "type":       "AlexaInterface",
  "interface":  "Alexa.PowerController",
  "version":    "3",
  "properties": {
    "supported":           [
      {
        "name": "power"
      }
    ],
    "proactivelyReported": False,
    "retrievable":         True
  }
}

ALEXA_POWER_LEVEL_INTERFACE = {
  "type":       "AlexaInterface",
  "interface":  "Alexa.PowerLevelController",
  "version":    "3",
  "properties": {
    "supported":           [
      {
        "name": "powerLevel"
      }
    ],
    "proactivelyReported": False,
    "retrievable":         True
  }
}

ALEXA_PERCENTAGE_INTERFACE = {
  "type":       "AlexaInterface",
  "interface":  "Alexa.PercentageController",
  "version":    "3",
  "properties": {
    "supported":           [
      {
        "name": "percentage"
      }
    ],
    "proactivelyReported": False,
    "retrievable":         True
  }
}

ALEXA_HEALTH_INTERFACE = {
  "type":       "AlexaInterface",
  "interface":  "Alexa.EndpointHealth",
  "version":    "3",
  "properties": {
    "supported":           [
      {
        "name": "connectivity"
      }
    ],
    "proactivelyReported": False,
    "retrievable":         True
  }
}

ALEXA_TEMPERATURE_INTERFACE = {
  "type":       "AlexaInterface",
  "interface":  "Alexa.TemperatureSensor",
  "version":    "3",
  "properties": {
    "supported":           [
      {
        "name": "temperature"
      }
    ],
    "proactivelyReported": False,
    "retrievable":         True
  }
}

ALEXA_LIGHT = 'LIGHT'
ALEXA_SMARTPLUG = 'SMARTPLUG'
ALEXA_SWITCH = 'SWITCH'
ALEXA_DOOR = 'DOOR'
ALEXA_SMARTLOCK = 'SMARTLOCK'
ALEXA_SPEAKERS = 'SPEAKERS'
ALEXA_TEMPERATURE_SENSOR = 'TEMPERATURE_SENSOR'
ALEXA_THERMOSTAT = 'THERMOSTAT'
ALEXA_TV = 'TV'
