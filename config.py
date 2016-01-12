import os

class Config:
    PICTURE_SAVE_DIRECTORY = '/home/pi/Pictures'
    COUCHDB_SERVER = 'http://localhost:5984/'
    COUCHDB_DATABASE = 'thermal'
    CELERY_BROKER_URL = 'amqp://localhost:5672'
    CELERY_RESULT_BACKEND = 'amqp://localhost:5672'
    STILL_IMAGE_WIDTH = 1600
    STILL_IMAGE_HEIGHT = 1200


    MAIL_SERVER = 'smtp.mail.yahoo.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    COUCHDB_DATABASE = 'thermal_testing'
    CELERY_ALWAYS_EAGER = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
