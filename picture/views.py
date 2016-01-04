import json

import couchdb
from flask import Blueprint, request, Response, current_app
from picture.services import find_pictures, find_picture

picture = Blueprint('picture', __name__)

@picture.route('/')
def list_pictures():
    pictures = find_pictures()
    return Response(json.dumps(pictures), status=200, mimetype='application/json')

@picture.route('/<picture_id>')
def get_picture(picture_id):
    picture_dict = find_picture(picture_id)
    if '_id' in picture_dict:
        return Response(json.dumps(picture_dict), status=200, mimetype='application/json')
    else:
        return Response('not found', status=404)
