import json
import uuid

from flask import Blueprint, request, Response, url_for

#from calibration.services import *
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
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_sets/<distortion_set_id>', methods=['GET'])
def get_distortion_set(distortion_set_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
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
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/distortion_pairs/<distortion_pair_id>', methods=['GET'])
def get_distortion_pair(distortion_pair_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
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
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@calibration.route('/calibration_sessions/<calibration_session_id>', methods=['GET'])
def get_calibration_sessions(calibration_session_id):
    try:
        return Response(json.dumps('x'), status=200, mimetype='application/json')
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
