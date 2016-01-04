import json

from flask import Blueprint, request, Response
from analysis.services import do_stuff

analysis = Blueprint('analysis', __name__)

@analysis.route('/')
def do_analysis_stuff():
    things = do_stuff()
    return Response(json.dumps(things), status=200, mimetype='application/json')
