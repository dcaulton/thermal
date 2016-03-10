import json

from flask import Blueprint, request, Response, url_for

from thermal.services import search_generic
from thermal.utils import get_document_with_exception, get_url_base


thermal = Blueprint('thermal', __name__)


@thermal.route('/')
def index():
    url_base = get_url_base()
    top_level_links = {
        'admin': url_base + url_for('admin.index'),
        'camera': url_base + url_for('camera.index'),
        'pictures': url_base + url_for('picture.list_pictures'),
        'merging': url_base + url_for('merging.index'),
        'analysis': url_base + url_for('analysis.index'),
        'calibration': url_base + url_for('calibration.index'),
        'docs': url_base + '/docs/_build/html',
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')

# TODO add a meta object to the response which indicates paging info
#  That should be pretty high level, it will be a wrapper around all our 'return Response' calls
def generic_list_view(document_type='', args_dict={}):
    try:
        # raise exception if no document type is not supplied
        documents = search_generic(document_type=document_type, args_dict=args_dict)
        return Response(json.dumps(documents), status=200, mimetype='application/json')
    except Exception as e:  # TODO add tests, bad paging info or strings that kill the map string could cause abends
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')

def generic_get_view(item_id='', document_type=''):
    '''
    Retrieves an document for the item of the specified type for the supplied id
    '''
    try:
        # raise exception if no item id is supplied
        # raise exception if no document type is supplied
        item_dict = get_document_with_exception(item_id, document_type)
        return Response(json.dumps(item_dict), status=200, mimetype='application/json')
    except Exception as e:  # TODO add tests, bad paging info or strings that kill the map string could cause abends
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
