# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-05-22 12:47:41
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-06-27 19:48:02

import collections
import requests

from flask import Flask
from flask import Response
from flask import redirect
from flask import render_template
from flask import request
from flask.ext.mongoengine import MongoEngine
from flask.ext.security import MongoEngineUserDatastore
from flask.ext.security import RoleMixin
from flask.ext.security import Security
from flask.ext.security import UserMixin
from flask.ext.security import auth_token_required
from flask.ext.security import current_user
from flask.ext.security import login_required

from OpenSSL import SSL
from flask_sslify import SSLify

#context = SSL.Context(SSL.SSLv23_METHOD)
#context.use_privatekey_file('certs/privkey.pem')
#context.use_certificate_file('certs/fullchain.pem')


from generators.dash_generator import dash_generator
from generators.dash_generator import refresh_generator

import json

from flask.ext.security.decorators import _get_unauthorized_response
from functools import wraps
from hashlib import sha256
from os import urandom

from mongoengine import *

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

# MongoDB Config
app.config['MONGODB_DB'] = 'ff_ui'
app.config['MONGODB_HOST'] = 'localhost'
app.config['MONGODB_PORT'] = 27017
app.config['WTF_CSRF_ENABLED'] = False

sslify = SSLify(app)


API_PATHS = {
  'routines' : 'http://localhost:6001/API/views/routine',
  'mode' : 'http://localhost:6001/API/mode',
  'device_vews' : 'http://localhost:6001/API/views/devices',
  'all_device_status' : 'http://localhost:6001/API/status/devices/all'
}



# Create database connection object
db = MongoEngine(app)

connect('auth_tokens', alias='auth_tokens')

class AuthToken(Document):
    user_id = StringField()
    token = StringField()
    app_name = StringField()

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])



# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Auth Token Check
def auth_token_required(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        #return fn(*args, **kwargs)
        print request.get_json()
        rToken = request.get_json().get("token")
        argsToken = request.args.get('token')
        #return _get_unauthorized_response()
        for token in AuthToken.objects:
            if rToken == token.token or argsToken == token.token:
                print token.user_id
                return fn(*args, **kwargs)
        return _get_unauthorized_response()
    return decorated

# Create a user to test with
@app.before_first_request
def create_user():
  for user in User.objects:
    if user.email == "admin":
      return
  user_datastore.create_user(email='admin', password='FireFlyPassword996')

#####################################################
#          WEB VIEWS
#####################################################

@app.route('/')
@login_required
def home():
    return redirect('/routines')

@app.route('/devices')
@login_required
def devices():
  devices = requests.get(API_PATHS['device_vews']).json()
  device_types= []
  for d, c in devices.iteritems():
    dType = c.get('type')
    if (dType is not None and dType not in device_types):
      device_types.append(dType)
  devices = collections.OrderedDict(sorted(devices.iteritems(), key=lambda elem: elem[1]['name']))
  dashButtons = dash_generator(devices)
  refreshJS = refresh_generator()
  return render_template('devices.html', devices=dashButtons, device_types=device_types, device_list=devices, js=refreshJS)


  '''
  dtype = 'switch'
  switches = {}
  devices = {}

  allViews = getAllDevices()
  allDevices = allViews.get('all_devices')
  shortcutGroups = allViews.get('dashboard_groups')
  filtered_devices = {}
  for name, device in allDevices.iteritems():
    if not isinstance(allDevices[name], bool):
      filtered_devices[name] = device
  allDevices = filtered_devices
  for name, options in collections.OrderedDict(sorted(allDevices.items(), key=lambda elem: elem[1]['title'])).iteritems():
    if options is not True and options is not False:
      if options.get('capabilities') is not None and dtype in options.get('capabilities') or dtype == 'all':
        switches[name] = options

  dtype = 'presence'
  presence = {}
  for name, options in collections.OrderedDict(sorted(allDevices.items(), key=lambda elem: elem[1]['title'])).iteritems():
    if options is not True and options is not False:
      if options.get('capabilities') is not None and dtype in options.get('capabilities') or dtype == 'all':
        presence[name] = options

  devices['switch'] = collections.OrderedDict(sorted(switches.items(), key=lambda elem: elem[1]['title']))
  devices['presence'] = collections.OrderedDict(sorted(presence.items(), key=lambda elem: elem[1]['title']))
  return render_template('devices.html', devices=devices, deviceTypeList=getDeviceCapabilities(allDevices), allViews=allViews)
  '''

  #return render_template('ui.html')


@app.route('/devices/views/<path:path>')
@login_required
def device_view(path):
  allDevices = requests.get(API_PATHS['all_device_status']).json()
  device = allDevices.get(path)
  device = json.dumps(device, sort_keys=True, indent=4, separators=(',', ': ')).replace('\n','</br>').replace('  ','&nbsp;')
  return "Still in development <code>" + device + "</code>"

@app.route('/dashboard')
@login_required
def dashbaord():
  '''
  date = datetime.now()
  cnn = 'http://rss.cnn.com/rss/cnn_topstories.rss'
  news = feedparser.parse(cnn)
  feed = []
  for item in news.get('items'):
    feed.append({'time':parser.parse(item['published']).astimezone(tz.gettz('America/Los_Angeles')).time().strftime("%I:%M %p"), 'title': item['title'], 'summary': item['summary_detail']['value'].split('<br')[0], 'link':item['links'][0]['href']})

  allViews = getAllDevices()
  allDevices = allViews.get('all_devices')
  weather = allDevices.get('UUID123')
  forecast = weather.get('value').get('forecast')
  forecast = {'value':forecast}
  current=weather.get('value').get('current')
  alerts = weather.get('value').get('alerts')

  for item in forecast.get('value'):
    item['icon'] = WEATHER_MAPPING.get(item.get('icon'))
  current['icon'] = WEATHER_MAPPING.get(current.get('icon'))
  
  return render_template('dashboard.html', weather=forecast, current=current, alerts=alerts, date=date, feed=feed)
  '''
  return render_template('ui.html')

@app.route('/shortcuts')
@login_required
def shortcuts():
  '''
  dtype = 'switch'
  switches = {}
  devices = {}

  allViews = getAllDevices()
  allDevices = allViews.get('all_devices')
  shortcutGroups = allViews.get('dashboard_groups')
  filtered_devices = {}
  for name, device in allDevices.iteritems():
    if not isinstance(allDevices[name], bool):
      filtered_devices[name] = device
  allDevices = filtered_devices
  for name, options in collections.OrderedDict(sorted(allDevices.items(), key=lambda elem: elem[1]['title'])).iteritems():
    if options is not True and options is not False:
      if options.get('capabilities') is not None and dtype in options.get('capabilities') or dtype == 'all':
        switches[name] = options
        pass
  devices['switch'] = collections.OrderedDict(sorted(switches.items(), key=lambda elem: elem[1]['title']))
  shortcuts = collections.OrderedDict(sorted(allViews.get('dashboard_groups').items()))
  return render_template('shortcuts.html', devices=devices, deviceTypeList=getDeviceCapabilities(allDevices), shortcuts=shortcuts, allDevices=allDevices)
  '''
  return render_template('ui.html')

@app.route('/routines')
@login_required
def routines():
  #TODO: This should just be requests.json
  routines = requests.get(API_PATHS['routines']).json()
  routines = collections.OrderedDict(sorted(routines.items(), key=lambda elem: elem[1]['id']))
  mode = requests.get(API_PATHS['mode']).text.title()
  return render_template('routines.html', routines=routines, mode=mode)

@app.route('/tokens')
@login_required
def listToken():
  tokens = {}
  for token in AuthToken.objects:
    tokens[token.app_name] = token.token 
  return render_template('tokens.html', tokens=tokens)

@app.route('/users')
@login_required
def listUsers():
  users = []
  for user in User.objects:
    users.append(user.email)
  return render_template('users.html', users=users)

@app.route('/settings')
@login_required
def settingsPage():
  return render_template('settings.html')


#####################################################
#          WEB UI API 
#####################################################

@app.route('/API/translator2', methods=['GET','POST'])
@login_required
def translator2():
  command = request.form.get('command')
  json_command = json.loads(command)
  new_command = {'myCommand':command}
  #json_command = json.dumps({'device':device, 'command': {command:value}})
  print json_command
  print new_command
  url = "http://localhost:6001/manual_command?myCommand=" + command
  requests.get(url)
  return redirect(request.referrer)

@app.route('/API/mode')
@login_required
def APIMode():
  mode = requests.get(API_PATHS['mode']).text.title()
  return mode

@app.route('/API/allDevices')
@login_required
def APIAllDevices():
  try:
    allDevices = requests.get(API_PATHS['all_device_status']).json()
    return json.dumps(allDevices)
  except:
    return ''

#####################################################
#          EXTERNAL API
#####################################################


@app.route('/api/get_token')
@login_required
def get_token():
  app_name = request.args.get('app_name')
  token = sha256(urandom(128)).hexdigest()
  t = AuthToken(user_id=str(current_user.id), token=token, app_name=app_name).save()
  return json.dumps({'token':token, 'app_name':app_name})

@app.route('/api/command', methods=['POST', 'GET'])
@auth_token_required
def api_test():
  print request.get_json().get('command')
  command = request.get_json().get('command')
  url = "http://localhost:6001/manual_command?myCommand=" + json.dumps(command)
  print url
  requests.get(url)
  # This is where I would forward the command to the innder API
  return "Okay"
  

#####################################################
#         QUICK PRESENCE
#####################################################

@auth_token_required
@app.route('/api/presence')
def quick_presence():
  device = str(request.args.get('d'))
  presence = bool2str(request.args.get('p'))
  command = {'device':device,'command':{'presence':presence}}
  url = "http://localhost:6001/manual_command?myCommand=" + json.dumps(command)
  requests.get(url)
  return "Okay"

def bool2str(s):
    if str(s).lower() in ['t', '1', 'true', 'present', 'entered', 'home', 'y', 'yes']:
        return True
    return False

#####################################################
#        QUICK PRESENCE
#####################################################

#####################################################
#         ECHO API
#####################################################

@app.route('/api/echo', methods=['GET','POST'])
@auth_token_required
def echo_api():
  command = json.dumps(request.get_json())
  print command
  url = "http://localhost:6001/api/echo"
  r = requests.post(url, json=command)
  # This is where I would forward the command to the innder API
  print str(r.text)
  return r.text + "\n"


#####################################################
#          END ECHO API
#####################################################


#####################################################
#          LETS ENCRYPT PATH
#####################################################

@app.route('/.well-known/acme-challenge/<path:path>')
def acme_challenge(path):
  return send_from_directory('well-known/acme-challenge', path, mimetype='text/plain')

@app.route('/add_user')
@login_required
def addUser():
  username = request.args.get('username')

  if username is not None and password is not None:
    user_datastore.create_user(email=username, password=password)
  return redirect('users')

@app.route('/remove_user')
@login_required
def removeUser():
  username = request.args.get('username')
  if username == 'admin':
    return redirect('users')
  User.objects(email=username).delete()
  return redirect('users')


if __name__ == '__main__':
  context = ('certs/fullchain.pem', 'certs/privkey.pem')
  app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=True)

