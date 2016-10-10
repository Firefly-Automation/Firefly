from flask import Flask
from core.firefly import app

@app.route('/')
def baseView():
  return "This is the root page"