class Config:
    PICTURE_SAVE_DIRECTORY = '/home/pi/Pictures'
    COUCHDB_SERVER = 'http://localhost:5984/'
    COUCHDB_DATABASE = 'thermal'
    CELERY_BROKER_URL = 'amqp://localhost:5672'
    CELERY_RESULT_BACKEND = 'amqp://localhost:5672'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    a=1

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
