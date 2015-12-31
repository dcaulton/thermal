import json

from celery import Celery
from flask import g, Blueprint, Flask, request, Response, current_app

crap = Blueprint('crap', __name__)

#app and current_app are unbound at this point, that's a bummer.  I don't have config yet!
#    gonna have to push that into some module and method downstram
#celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery = Celery('tasks', broker='amqp://')

@crap.route('/')
def index():
    data = {'dingo': 'dinner'}
    do_thing()
    return Response(json.dumps(data), status=200, mimetype='application/json')

@crap.route('/later')
@celery.task
def later():
    data = {'dingo': 'midnight snack'}
#    task = do_thing.delay()
    task = do_thing.apply_async(countdown=10)
    return Response(json.dumps(data), status=200, mimetype='application/json')

@celery.task
def do_thing():
    print 'chacha'
