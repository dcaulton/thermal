import json

import couchdb
from flask import Blueprint, request, Response

from picture.services import find_pictures, find_picture
from thermal.exceptions import NotFoundError

picture = Blueprint('picture', __name__)


# TODO add a meta object to the response which indicates paging info
#  That should be pretty high level, it will be a wrapper around all our 'return Response' calls
@picture.route('/')
def list_pictures():
    '''
    Lists all pictures
    '''
    search_dict = {}
    for key in request.args.keys():
        search_dict[key] = request.args[key]
    pictures = find_pictures(search_dict)
    return Response(json.dumps(pictures), status=200, mimetype='application/json')


@picture.route('/<picture_id>')
def get_picture(picture_id):
    '''
    Retrieves a picture for the supplied id
    '''
    try:
        picture_dict = find_picture(picture_id)
    except NotFoundError as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
    return Response(json.dumps(picture_dict), status=200, mimetype='application/json')
