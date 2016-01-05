import json

import couchdb
from flask import Blueprint, request, Response

from picture.services import find_pictures, find_picture
from thermal.exceptions import NotFoundError

picture = Blueprint('picture', __name__)

@picture.route('/')
def list_pictures():
    pictures = find_pictures(request.args)
    return Response(json.dumps(pictures), status=200, mimetype='application/json')

@picture.route('/<picture_id>')
def get_picture(picture_id):
    try:
        picture_dict = find_picture(picture_id)
    except NotFoundError as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
    return Response(json.dumps(picture_dict), status=200, mimetype='application/json')
