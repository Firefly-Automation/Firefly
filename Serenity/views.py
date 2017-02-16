from Serenity import app, API_PATHS
from Serenity.serenity import firefly_get_request
from flask.ext.security import login_required
import json

@app.route('/')
def root_page():
  return 'Hello World'


@app.route('/API/status')
@login_required
def api_status():
  return json.dumps(firefly_get_request(API_PATHS['STATUS']), indent=4, sort_keys=True)



