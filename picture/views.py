import json

from flask import Blueprint, Response

from thermal.services import search_generic
from thermal.utils import gather_and_enforce_request_args, get_document_with_exception

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
        pictures = search_generic(document_type='picture')
        return Response(json.dumps(pictures), status=200, mimetype='application/json')
    except Exception as e:  # TODO add tests, bad paging info or strings that kill the map string could cause abends
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@picture.route('/<picture_id>')
def get_picture(picture_id):
    '''
    Retrieves a picture for the supplied id
    '''
    try:
        picture_dict = get_document_with_exception(picture_id, 'picture')
        return Response(json.dumps(picture_dict), status=200, mimetype='application/json')
    except Exception as e:  # TODO add tests, bad paging info or strings that kill the map string could cause abends
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
