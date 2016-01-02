import socket

import couchdb
from flask import g, Flask

from admin.controller import admin
from camera.controller import camera
from crap.controller import crap
from config import config, Config
from picture.controller import picture

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    app.config['HOSTNAME'] = socket.gethostname()

    register_blueprints(app)
    register_before_request(app)

    return app

def register_before_request(app):
    @app.before_request
    def before_request():
        couch = couchdb.Server()
        db = couch['thermal']
        g.db = db

def register_blueprints(app):
    app.register_blueprint(camera, url_prefix='/camera')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(picture, url_prefix='/pictures')
    app.register_blueprint(crap, url_prefix='/crap')
