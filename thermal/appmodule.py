import socket

from celery import Celery
import couchdb
from flask import g, Flask
from flask.ext.mail import Mail

from config import config, Config

celery = Celery('thermal', broker=Config.CELERY_BROKER_URL)
mail = Mail()


def create_app(config_name='development'):
    app = Flask('thermal')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    app.config['HOSTNAME'] = socket.gethostname()

    register_blueprints(app)
    register_mail(app)

#    @app.before_request
#    def before_request():
#        couch = couchdb.Server()
#        db = couch['thermal']
#        g.db = db
#
    return app


def register_mail(app):
    mail = Mail(app)


def register_db(app):
    couch = couchdb.Server()
    if hasattr(app, 'config'):
        if 'COUCHDB_DATABASE' in app.config:
            try:
                app.db = couch[app.config['COUCHDB_DATABASE']]
            except couchdb.http.ResourceNotFound as e:
                couch.create(app.config['COUCHDB_DATABASE'])
                app.db = couch[app.config['COUCHDB_DATABASE']]
        else:
            raise Exception('No value for COUCHDB_DATABASE in the app config')
    else:
        raise Exception('Trying to register db with an app has no config')


def register_blueprints(app):
    from admin.views import admin
    from camera.views import camera
    from thermal.views import thermal
    from picture.views import picture
    from merging.views import merging
    from analysis.views import analysis
    from calibration.views import calibration
    app.register_blueprint(camera, url_prefix='/api/v1/camera')
    app.register_blueprint(admin, url_prefix='/api/v1/admin')
    app.register_blueprint(picture, url_prefix='/api/v1/pictures')
    app.register_blueprint(merging, url_prefix='/api/v1/merging')
    app.register_blueprint(analysis, url_prefix='/api/v1/analysis')
    app.register_blueprint(calibration, url_prefix='/api/v1/calibration')
    app.register_blueprint(thermal, url_prefix='/api/v1')


def make_celery(app):
    celery = Celery('thermal', broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
