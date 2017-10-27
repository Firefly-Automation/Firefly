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
