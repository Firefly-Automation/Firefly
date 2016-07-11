import flask
from flask import request
from flask_socketio import SocketIO

app = flask.Flask(__name__,static_url_path='/static',static_folder='static')
app.secret_key = 'super secret string'  # Change this!
app.config['SECRET_KEY'] = 'secret!'
app.config['port'] =6002
socketio = SocketIO(app)


import flask.ext.login as flask_login
from flask import request, jsonify, redirect, render_template
import requests
import json
import time
import collections
import operator
import templates
from datetime import datetime
from dateutil import tz, parser
import feedparser

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

# Our mock database.
users = {'admin': {'pw': 'admin'}, 'user':{'pw':'FireFlyPassword996'}}

WEATHER_MAPPING = {
None             :  'wi-na',
'clear-day'      :  'wi-forecast-io-clear-day',
'day-sunny'      :  'wi-forecast-io-clear-day',
'night-clear'    :  'wi-forecast-io-clear-night',
'rain'           :  'wi-forecast-io-rain',
'snow'           :  'wi-forecast-io-snow',
'sleet'          :  'wi-forecast-io-sleet',
'strong-wind'    :  'wi-forecast-io-wind',
'fog'            :  'wi-forecast-io-fog',
'cloudy'         :  'wi-forecast-io-cloudy',
'partly-cloudy-day'  :  'wi-forecast-io-partly-cloudy-day',
'day-cloudy'     :  'wi-forecast-io-partly-cloudy-day',
'night-cloudy'   :  'wi-forecast-io-partly-cloudy-night',
'partly-cloudy-night'   :  'wi-forecast-io-partly-cloudy-night',
'hail'           :  'wi-forecast-io-hail',
'thunderstorm'   :  'wi-forecast-io-thunderstorm',
'tornado'        :  'wi-forecast-io-tornado',
}

API_PATHS = {
  'routines' : 'http://localhost:6001/API/views/routine',
  'mode' : 'http://localhost:6001/API/mode'
}


class User(flask_login.UserMixin):
  pass


@login_manager.user_loader
def user_loader(email):
  if email not in users:
    return

  user = User()
  user.id = email
  return user


@login_manager.request_loader
def request_loader(request):
  email = request.form.get('email')
  if email not in users:
    return

  user = User()
  user.id = email

  # DO NOT ever store passwords in plaintext and always compare password
  # hashes using constant-time comparison!
  user.is_authenticated = request.form['pw'] == users[email]['pw']

  return user

@app.route('/')
def root():
  return flask.redirect('/login')

@flask_login.login_required
@app.route('/login', methods=['GET', 'POST'])
def login():
  return flask.redirect('/dashboard')

@app.route('/loginPage', methods=['GET', 'POST'])
def loginPage():
  if flask.request.method == 'GET':
    return render_template('login.html')

  email = flask.request.form['email']
  if flask.request.form['pw'] == users[email]['pw']:
    user = User()
    user.id = email
    if flask.request.form.get('remember'):
      user.remember = True
    flask_login.login_user(user)
    return flask.redirect('/dashboard')

  return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
  return 'Logged in as: ' + flask_login.current_user.id

@app.route('/API/translator', methods=['GET','POST'])
@flask_login.login_required
def translator():
  device = request.form.get('device')
  command = request.form.get('command')
  value = request.form.get('value')
  if not device:
    device = request.args.get('device')
    command = request.args.get('command')
    value = request.args.get('value')

  json_command = json.dumps({'device':device, 'command': {command:value}})
  requests.post('http://localhost:5000/API/control', data=json_command)
  time.sleep(1)
  return redirect(request.referrer)

@app.route('/API/translator2', methods=['GET','POST'])
@flask_login.login_required
def translator2():
  command = request.form.get('command')
  json_command = json.loads(command)
  new_command = {'myCommand':command}
  #json_command = json.dumps({'device':device, 'command': {command:value}})
  url = "http://localhost:6001/manual_command?myCommand=" + command
  requests.get(url)
  time.sleep(1)
  return redirect(request.referrer)

@app.route('/devices/<path:dtype>')
@flask_login.login_required
def deviceView(dtype):
  return generateDeviceView(dtype)

@app.route('/groups/<path:groupName>')
@flask_login.login_required
def groupView(groupName):
  return generateGroupView(groupName)

@app.route('/test')
@flask_login.login_required
def test():
  return render_template('test.html')

@app.route('/devices')
@flask_login.login_required
def devices():
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
  return render_template('ui.html')

@app.route('/dashboard')
@flask_login.login_required
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
@flask_login.login_required
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
@flask_login.login_required
def routines():
  #TODO: This should just be requests.json
  routines = requests.get(API_PATHS['routines']).json()
  routines = collections.OrderedDict(sorted(routines.items(), key=lambda elem: elem[1]['id']))
  mode = requests.get(API_PATHS['mode']).text.title()
  return render_template('routines.html', routines=routines, mode=mode)

@app.route('/API/mode')
@flask_login.login_required
def APIMode():
  mode = requests.get(API_PATHS['mode']).text.title()
  return mode

@app.route('/logout')
@flask_login.login_required
def logout():
  flask_login.logout_user()
  return flask.redirect('/login')

@login_manager.unauthorized_handler
def unauthorized_handler():
  return flask.redirect('/loginPage')

@app.route('/API/allDevices')
def getAllDevicesRaw():
  views = requests.get('http://localhost:5000/API/getAllViews')
  return views.text #json.loads(views.text)

def getAllDevices():
  views = requests.get('http://localhost:5000/API/getAllViews')
  return json.loads(views.text)

def getDeviceCapabilities(devices):
  capabilities = []
  for name, info in devices.iteritems():
    try:
      for c in info.get('capabilities'):
        if c not in capabilities:
          capabilities.append(c)
    except:
      print name
  return capabilities


if __name__ == '__main__':
  app.run( port=6002,debug=True,use_reloader=True, host='0.0.0.0')
