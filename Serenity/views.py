from Serenity import app, API_PATHS
from Serenity.serenity import firefly_get_request
from flask.ext.security import login_required, current_user
import json

@app.route('/')
def root_page():
  return 'Hello World'


@app.route('/API/status')
@login_required
def api_status():
  return json.dumps(firefly_get_request(API_PATHS['STATUS']), indent=4, sort_keys=True)

@app.route('/API/mode')
@login_required
def api_mode():
  mode = firefly_get_request(API_PATHS['STATUS']).get('mode')
  if mode is None:
    return 'ERROR'
  return mode

@app.route('/API/time')
@login_required
def api_time():
  time = firefly_get_request(API_PATHS['STATUS']).get('time')
  if time is None:
    return 'ERROR'
  return time.get('str')


@app.route('/who')
@login_required
def who():
  return current_user.username
