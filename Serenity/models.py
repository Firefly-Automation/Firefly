import logging
from functools import wraps
from hashlib import sha256
from os import urandom

from flask import request
from flask.ext.security import RoleMixin, SQLAlchemyUserDatastore, Security, UserMixin
from flask.ext.security.decorators import _get_unauthorized_response
from flask.ext.security.forms import LoginForm
from flask.ext.sqlalchemy import SQLAlchemy
from flask_security import current_user
from flask_security.utils import encrypt_password
from wtforms import StringField
from wtforms.validators import InputRequired

from Serenity import app

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class AuthToken(db.Model):
  user_id = db.Column(db.String(255))
  token = db.Column(db.String(255), primary_key=True)
  app_name = db.Column(db.String(255))


class Role(db.Model, RoleMixin):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255), unique=True)
  password = db.Column(db.String(255))
  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  theme = db.Column(db.String(255))
  roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))


class ExtendedLoginForm(LoginForm):
  email = StringField('Username', [InputRequired()])


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    login_form=ExtendedLoginForm)


# Auth Token Check
def auth_token_required(fn):
  @wraps(fn)
  def decorated(*args, **kwargs):
    # return fn(*args, **kwargs)
    rToken = None
    if request.get_json():
      rToken = request.get_json().get("token")
    argsToken = request.args.get('token')
    # return _get_unauthorized_response()
    for token in AuthToken.query.all():
      if rToken == token.token or argsToken == token.token:
        logging.debug(token.user_id)
        return fn(*args, **kwargs)
    return _get_unauthorized_response()

  return decorated


# Create a user to test with


@app.before_first_request
def create_user():
  adminUser = False
  db.create_all()
  for user in User.query.all():
    if user.username == 'admin':
      adminUser = True
  if not adminUser:
    user_datastore.create_user(
      username='admin', password=encrypt_password('FireflyPassword1234'))
    db.session.commit()


def add_user(username, password):
  userInDB = False
  for user in User.query.all():
    print(user.username)
    if user.username == username:
      userInDB = True
  if not userInDB:
    user_datastore.create_user(
      username=username, password=encrypt_password(password))
    db.session.commit()
    return True
  return False


def remove_user(username):
  userInDB = False
  userObject = None
  for user in User.query.all():
    print(user.username)
    if user.username == username:
      userInDB = True
      userObject = user
  if userInDB and username != 'admin':
    user_datastore.delete_user(userObject)
    db.session.commit()
    return True
  return False


def add_token(app_name):
  token = sha256(urandom(128)).hexdigest()
  db.session.add(AuthToken(user_id=str(current_user.id), token=token, app_name=app_name))
  db.session.commit()
  return token

def set_user_theme(theme):
  user = db.session.query(User).get(current_user.id)
  user.theme = theme
  db.session.commit()


def remove_token(token):
  AuthToken.query.filter_by(token=token).delete()
  db.session.commit()