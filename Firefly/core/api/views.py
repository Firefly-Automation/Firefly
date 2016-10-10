from flask import Flask

@app.route('/')
def baseView():
  return "This is the root page"