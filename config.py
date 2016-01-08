class Config:
    PICTURE_SAVE_DIRECTORY = '/home/pi/Pictures'
    COUCHDB_SERVER = 'http://localhost:5984/'
    COUCHDB_DATABASE = 'thermal'
    CELERY_BROKER_URL = 'amqp://localhost:5672'
    CELERY_RESULT_BACKEND = 'amqp://localhost:5672'
    STILL_IMAGE_WIDTH = 1600
    STILL_IMAGE_HEIGHT = 1200

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    COUCHDB_DATABASE = 'thermal_testing'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
