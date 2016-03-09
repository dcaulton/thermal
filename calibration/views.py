import json
import uuid

from flask import Blueprint, request, Response, url_for

from calibration.services import (find_calibration_sessions,
                                  get_calibration_session_document,
                                  find_distortion_pairs,
                                  get_distortion_pair_document,
                                  find_distortion_sets,
                                  get_distortion_set_document)
from thermal.utils import get_url_base

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
    generic_list_view(document_type='distortion_set')


@calibration.route('/distortion_sets/<distortion_set_id>', methods=['GET'])
def get_distortion_set(distortion_set_id):
    try:
        distortion_set_dict = get_distortion_set_document(distortion_set_id)
        return Response(json.dumps(distortion_set_dict), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_sets/<distortion_set_id>', methods=['PUT'])
def update_distortion_set(distortion_set_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_sets/<distortion_set_id>', methods=['POST'])
def create_distortion_set(distortion_set_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_pairs')
def list_distortion_pairs():
    '''
    Lists all distortion pairs
    Supports paging and filtering on any attribute via get parms
    '''
    generic_list_view(document_type='distortion_pair')


@calibration.route('/distortion_pairs/<distortion_pair_id>', methods=['GET'])
def get_distortion_pair(distortion_pair_id):
    try:
        distortion_pair_dict = get_distortion_pair_document(distortion_pair_id)
        return Response(json.dumps(distortion_pair_dict), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_pairs/<distortion_pair_id>', methods=['PUT'])
def update_distortion_pairs(distortion_pair_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_pairs/<distortion_pair_id>', methods=['POST'])
def create_distortion_pair(distortion_pair_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/calibration_sessions')
def list_calibration_sessions():
    '''
    Lists all calibration sessions
    Supports paging and filtering on any attribute via get parms
    '''
    generic_list_view(document_type='calibration_session')


@calibration.route('/calibration_sessions/<calibration_session_id>', methods=['GET'])
def get_calibration_sessions(calibration_session_id):
    try:
        calibration_session_dict = get_calibration_session_document(calibration_session_id)
        return Response(json.dumps(calibration_session_dict), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/calibration_sessions/<calibration_session_id>', methods=['PUT'])
def update_calibration_session(calibration_session_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/calibration_sessions/<calibration_session_id>', methods=['POST'])
def create_calibration_session(calibration_session_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
