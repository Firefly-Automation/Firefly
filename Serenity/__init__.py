from configparser import ConfigParser

from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from Firefly.const import SERENITY_CONFIG, SERENITY_CONFIG_FILE

app = Flask(__name__)

# This is a fix for https redirects
app.wsgi_app = ProxyFix(app.wsgi_app)


# Get config values
config = ConfigParser()
config.read(SERENITY_CONFIG_FILE)
serenity_config = config[SERENITY_CONFIG]

serenity_host = serenity_config.get('host', '0.0.0.0')
serenity_port = serenity_config.getint('port', 8080)
serenity_debug = serenity_config.getbool('debug', False)



