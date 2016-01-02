import json

from celery import Celery
from flask import g, Blueprint, Flask, request, Response, current_app
from admin.controller import get_settings_document



#app and current_app are unbound at this point, that's a bummer.  I don't have config yet!
#    gonna have to push that into some module and method downstram
#celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery = Celery('tasks', broker='amqp://')

@celery.task
def do_thing():
    import pdb; pdb.set_trace()
    print 'chacha1'
    print str(g.__dict__)
    print 'chacha2'
    settings = get_settings_document()
    print str(settings)
