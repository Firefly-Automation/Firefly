from Firefly.core import Firefly
from Firefly.helpers.settings import Settings
from Firefly.const import CONFIG_FILE

from Firefly.api import FireflyCoreAPI

from Firefly.core import app


def main():
  # Get settings for Firefly.
  firefly_settings = Settings(CONFIG_FILE)

  # Initialize Firefly.
  firefly = Firefly(firefly_settings)

  # Initialize core API functions.
  core_api = FireflyCoreAPI(firefly, app)
  core_api.setup_api()

  # Start Firefly.
  firefly.start()

if __name__ == '__main__':
  main()
