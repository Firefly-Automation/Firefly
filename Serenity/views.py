from Serenity import app, API_PATHS
from Serenity.serenity import firefly_get_request
from flask.ext.security import login_required, current_user
from flask import render_template, send_from_directory, redirect

from Serenity.models import set_user_theme
import json


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/tpl/<path:path>')
def send_tpl(path):
    return send_from_directory('templates', path)

@app.route('/')
@login_required
def root_page():
  return render_template('base.html')

@app.route('/sample')
@login_required
def sample_page():
  return render_template('sample.html')


@app.route('/settings')
@login_required
def settings():
  return render_template('settings.html')

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
  theme = current_user.theme
  if theme is None:
    theme = 'default'
  return current_user.username + '\n' + theme

@app.route('/theme')
@login_required
def get_theme():
  theme = current_user.theme
  if theme is None or theme == 'undefined':
    theme = 'default'
  return theme


@app.route('/theme/<path:path>')
@login_required
def set_theme(path):
  set_user_theme(path)
  return path


