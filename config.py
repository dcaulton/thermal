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

    S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    COUCHDB_DATABASE = 'thermal_testing'
    CELERY_ALWAYS_EAGER = True
    PICTURE_SAVE_DIRECTORY = '/tmp/pictures_test'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        if not os.path.isdir(cls.PICTURE_SAVE_DIRECTORY):
            os.mkdir(cls.PICTURE_SAVE_DIRECTORY)



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
