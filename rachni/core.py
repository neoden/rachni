from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager

mongo = PyMongo()

login_manager = LoginManager()