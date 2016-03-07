import json

import couchdb
from flask import Blueprint, request, Response

from picture.services import find_pictures, find_picture
from thermal.exceptions import NotFoundError
from thermal.utils import gather_and_enforce_request_args

picture = Blueprint('picture', __name__)


# TODO add a meta object to the response which indicates paging info
#  That should be pretty high level, it will be a wrapper around all our 'return Response' calls
@picture.route('/')
def list_pictures():
    '''
    Lists all pictures
    Supports paging and filtering on any picture attribute via get parms
    '''
    try:
        search_dict = gather_and_enforce_request_args(['ANY_SEARCHABLE'])
        pictures = find_pictures(search_dict)
        return Response(json.dumps(pictures), status=200, mimetype='application/json')
    except Exception as e:  # TODO add tests, bad paging info or strings that kill the map string could cause abends
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@picture.route('/<picture_id>')
def get_picture(picture_id):
    '''
    Retrieves a picture for the supplied id
    '''
    try:
        picture_dict = find_picture(picture_id)
        return Response(json.dumps(picture_dict), status=200, mimetype='application/json')
    except Exception as e:  # TODO add tests, bad paging info or strings that kill the map string could cause abends
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
