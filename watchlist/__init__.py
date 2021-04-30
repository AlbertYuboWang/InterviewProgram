# -*- coding: utf-8 -*-
import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import pymysql 
pymysql.install_as_MySQLdb()

from flask_cache import Cache

config = {
  'CACHE_TYPE': 'redis',
  'CACHE_REDIS_HOST': '127.0.0.1',
  'CACHE_REDIS_PORT': 6379,
  'CACHE_REDIS_DB': '',
  'CACHE_REDIS_PASSWORD': ''
}


app = Flask(__name__)
cache = Cache(app, config=config)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
prefix = 'mysql://'
MYSQL_PORT = "root:password@localhost:3306"
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(MYSQL_PORT, os.getenv('DATABASE_NAME', 'data_db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'login'
# login_manager.login_message = 'Your custom message'


@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)


from watchlist import views, errors, commands
