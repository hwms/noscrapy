from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap
from flask_debug import Debug

from .frontend.controllers import frontend
from .nav.controllers import nav


def create_app(configfile=None):
    app = Flask(__name__)
    # app.config.from_object('noscrapy.app.config')
    AppConfig(app)
    Bootstrap(app)
    Debug(app)
    app.register_blueprint(frontend)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    nav.init_app(app)
    return app
