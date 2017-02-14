from Serenity import app

@app.route('/')
def root_page():
  return 'Hello World'