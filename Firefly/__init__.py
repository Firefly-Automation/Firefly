from Firefly.util.error_code_util import ErrorCodes
error_codes = ErrorCodes('Firefly/util/error_codes.json')

from Firefly.helpers.logging import FireflyLogging
logging = FireflyLogging()

from Firefly.helpers.alias import Alias
from Firefly.helpers.scheduler import Scheduler

aliases = Alias()
scheduler = Scheduler()


from Firefly.const import ALEXA_OFF, ALEXA_ON
ALEXA_CONST = [ALEXA_ON, ALEXA_OFF]