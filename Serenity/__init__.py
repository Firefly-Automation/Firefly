from configparser import ConfigParser

from flask import Flask
from flask.ext.security import Security
from werkzeug.contrib.fixers import ProxyFix

from Firefly.const import SERENITY_CONFIG_SECTION, FIREFLY_CONFIG_SECTION, SERENITY_CONFIG_FILE

app = Flask(__name__, static_url_path='')

# This is a fix for https redirects
app.wsgi_app = ProxyFix(app.wsgi_app)


# Get config values
config = ConfigParser()
config.read(SERENITY_CONFIG_FILE)
serenity_config = config[SERENITY_CONFIG_SECTION]

serenity_host = serenity_config.get('host', '0.0.0.0')
serenity_port = serenity_config.getint('port', 8080)
serenity_debug = serenity_config.getboolean('debug', False)

firefly_config = config[FIREFLY_CONFIG_SECTION]
firefly_host = firefly_config.get('host', 'http://localhost')
firefly_port = firefly_config.getint('port', 6002)
firefly_simulate = firefly_config.getboolean('simulate', False)


# DATABASE LINK FOR USERS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Serenity_Sample.db'

# Let flask-security use username not email
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'username'

app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_SEND_PASSWORD_CHANGE_EMAIL'] = False
app.config['SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL'] = False

# TODO: Generate this on install
app.config['SECRET_KEY'] = 'super-secret'

app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
# TODO: Generate this on install
app.config['SECURITY_PASSWORD_SALT'] = 'MyPasswordSalt'

firefly_address = '%s:%d' % (firefly_host, firefly_port)

API_PATHS = {
  'STATUS': '%s/API/rest/status' % firefly_address
}

if firefly_simulate:
  API_PATHS = {
    'STATUS': 'Serenity/simulation_files/status.json'
  }


import  Serenity.models
import Serenity.views



