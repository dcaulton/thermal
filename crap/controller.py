import json

from flask import g, Blueprint, Flask, request, Response, current_app
import crap.service as cs


crap = Blueprint('crap', __name__)

@crap.route('/')
def index():
    data = {'dingo': 'dinner'}
    do_thing()
    return Response(json.dumps(data), status=200, mimetype='application/json')

@crap.route('/later')
def later():
    data = {'carolina dog': 'breakfast'}
#    task = do_thing()
    cs.do_thing.apply_async(countdown=3)
    return Response(json.dumps(data), status=200, mimetype='application/json')
