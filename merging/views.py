import json

from flask import Blueprint, request, Response
from merging.services import do_stuff

merging = Blueprint('merging', __name__)

@merging.route('/')
def do_merging_thing():
    the_thing = do_stuff()
    return Response(json.dumps(the_thing), status=200, mimetype='application/json')
