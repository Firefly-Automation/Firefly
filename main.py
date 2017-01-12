from Firefly.core import Firefly
from Firefly.helpers.settings import Settings

from Firefly.api import FireflyCoreAPI


def main():
  # Get settings for Firefly.
  firefly_settings = Settings('firefly.config')

  # Initialize Firefly.
  firefly = Firefly(firefly_settings)

  # Initialize core API functions.
  core_api = FireflyCoreAPI(firefly)
  core_api.setup_api()

  # Start Firefly.
  firefly.start()

if __name__ == '__main__':
  main()