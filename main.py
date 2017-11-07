from Firefly.api import FireflyCoreAPI
from Firefly.const import CONFIG_FILE
from Firefly.core.core import Firefly, app
from Firefly.helpers.settings import Settings
from logging.handlers import RotatingFileHandler




# Disable debug logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s\t%(levelname)s:\t%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("pyrebase").setLevel(logging.WARNING)
logging.getLogger("lightify").setLevel(logging.WARNING)




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
