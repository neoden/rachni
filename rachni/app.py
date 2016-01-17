import os
import json
from flask import Flask
from redis import StrictRedis

from rachni.core import login_manager, redis, db
from rachni.main import models
from config import Config


def create_app(cfg=None):
    app = Flask(__name__)

    load_config(app, cfg)

    redis.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)

    from rachni.main import mod as main_bp
    app.register_blueprint(main_bp)

    return app


def load_config(app, cfg=None):
    app.config.from_object(
        Config.from_file(
            os.path.join(app.root_path, 'config.json')))

    local_config_path = os.path.join(app.root_path, 'config.local.json')

    if os.path.isfile(local_config_path):
        app.config.from_object(
            Config.from_file(local_config_path))

    if cfg is None and 'RACHNI_CFG' in os.environ:
        cfg = os.environ['RACHNI_CFG']

    if cfg is not None:
        app.config.from_object(Config.from_file(cfg))

    # for k, v in app.config.items():
    #     print('{} = {}'.format(k, v))
