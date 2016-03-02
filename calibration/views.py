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
