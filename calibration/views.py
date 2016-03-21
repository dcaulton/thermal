import json
import uuid

from flask import Blueprint, request, Response, url_for

from calibration.services import (get_calibration_session_document,
                                  get_distortion_pair_document,
                                  get_distortion_set_document)
from thermal.services import save_generic
from thermal.utils import (cast_uuid_to_string,
                           gather_and_enforce_request_args,
                           get_url_base,
                           item_exists)
from thermal.views import (generic_get_view,
                           generic_list_view,
                           generic_save_view)

calibration = Blueprint('calibration', __name__)


@calibration.route('/')
def index():
    '''
    Lists top level endpoints for calibration
    '''
    url_base = get_url_base()
    top_level_links = { 
        'distortion_sets': url_base + url_for('calibration.list_distortion_sets'),
        'distortion_pairs': url_base + url_for('calibration.list_distortion_pairs'),
        'calibration_sessions': url_base + url_for('calibration.list_calibration_sessions'),
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')


@calibration.route('/distortion_sets/')
def list_distortion_sets():
    '''
    Lists all distortion sets
    Supports paging and filtering on any attribute via get parms
    '''
    return generic_list_view(document_type='distortion_set')


@calibration.route('/distortion_sets/<distortion_set_id>', methods=['GET'])
def get_distortion_set(distortion_set_id):
    '''
    Fetches an individual distortion set
    '''
    return generic_get_view(item_id=distortion_set_id, document_type='distortion_set')


@calibration.route('/distortion_sets/<distortion_set_id>', methods=['PUT'])
def update_distortion_set(distortion_set_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_sets', methods=['POST'])
def create_distortion_set():
    return generic_save_view(document_type='distortion_set')


@calibration.route('/distortion_pairs')
def list_distortion_pairs():
    '''
    Lists all distortion pairs
    Supports paging and filtering on any attribute via get parms
    '''
    return generic_list_view(document_type='distortion_pair')


@calibration.route('/distortion_pairs/<distortion_pair_id>', methods=['GET'])
def get_distortion_pair(distortion_pair_id):
    '''
    Fetches an individual distortion pair
    '''
    return generic_get_view(item_id=distortion_pair_id, document_type='distortion_pair')


@calibration.route('/distortion_pairs/<distortion_pair_id>', methods=['PUT'])
def update_distortion_pairs(distortion_pair_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_pairs', methods=['POST'])
def create_distortion_pair():
    try:
        if 'distortion_set_id' not in request.json:
            distortion_set_id = cast_uuid_to_string(uuid.uuid4())
            request.json['distortion_set_id'] = distortion_set_id
        else:
            distortion_set_id = request.json['distortion_set_id']

        if not item_exists(distortion_set_id, 'distortion_set'):
            distortion_set_dict = {'_id': distortion_set_id, 'type': 'distortion_set'}
            save_generic(distortion_set_dict, 'distortion_set')

        # TODO add a lot more tests to the request json, we need start_x, y, end_x, y and they need to be ints, range tests, etc
        #  ^^^^^ have this be a validation function which is optionally passed to save_generic
        return_value = generic_save_view(document_type='distortion_pair')
        return return_value
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/calibration_sessions')
def list_calibration_sessions():
    '''
    Lists all calibration sessions
    Supports paging and filtering on any attribute via get parms
    '''
    return generic_list_view(document_type='calibration_session')


@calibration.route('/calibration_sessions/<calibration_session_id>', methods=['GET'])
def get_calibration_session(calibration_session_id):
    '''
    Fetches an individual calibration session
    '''
    return generic_get_view(item_id=calibration_session_id, document_type='calibration_session')


@calibration.route('/calibration_sessions/<calibration_session_id>', methods=['PUT'])
def update_calibration_session(calibration_session_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/calibration_sessions', methods=['POST'])
def create_calibration_session():
    return generic_save_view(document_type='calibration_session')
