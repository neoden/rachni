from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager
from flask.ext.redis import FlaskRedis

mongo = PyMongo()

login_manager = LoginManager()

redis = FlaskRedis()