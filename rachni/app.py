import os
from flask import Flask


def create_app(cfg=None):
    app = Flask(__name__)

    load_config(app, cfg)

    from rachni.core import mongo
    mongo.init_app(app)

    from rachni.core import login_manager
    login_manager.init_app(app)

    from rachni.main import mod as main_bp
    app.register_blueprint(main_bp)

    return app


def load_config(app, cfg=None):
    app.config.from_pyfile('config.py')

    if os.path.isfile('config.local.py'):
        app.config.from_pyfile('config.local.py')

    if cfg is None and 'RACHNI_CFG' in os.environ:
        cfg = os.environ['RACHNI_CFG']

    if cfg is not None:
        app.config.from_pyfile(cfg)
