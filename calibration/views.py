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
#        'scale_image': url_base + url_for('analysis.call_scale_image'),
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')


@calibration.route('/distortion_set')
def get_distortion_set(methods=['GET']):
    pass


@calibration.route('/distortion_set')
def update_distortion_set(methods=['PUT']):
    pass


@calibration.route('/distortion_set')
def create_distortion_set(methods=['POST']):
    pass


@calibration.route('/distortion_pair')
def get_distortion_pair(methods=['GET']):
    pass


@calibration.route('/distortion_pair')
def update_distortion_pairt(methods=['PUT']):
    pass


@calibration.route('/distortion_pair')
def create_distortion_pair(methods=['POST']):
    pass


@calibration.route('/calibration_session')
def get_calibration_session(methods=['GET']):
    pass


@calibration.route('/calibration_session')
def update_calibration_session(methods=['PUT']):
    pass


@calibration.route('/calibration_session')
def create_calibration_session(methods=['POST']):
    pass
