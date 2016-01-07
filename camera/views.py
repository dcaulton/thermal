import json
import time
import uuid

from flask import Blueprint, request, Response, current_app

from admin.services import get_settings_document
from camera.tasks import take_picam_still, take_thermal_still, both_still_chain

camera = Blueprint('camera', __name__)

@camera.route('/')
def index():
    return "Camera"

@camera.route('/picam_still')
def picam_still():
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()
    repeat = get_repeat_parameter()
    ret_dict = take_picam_still(snap_id=snap_id, group_id=group_id, delay=delay, repeat=repeat)
    return Response(json.dumps(ret_dict), status=202, mimetype='application/json')

@camera.route('/thermal_still')
def thermal_still():
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()
    repeat = get_repeat_parameter()
    scale_image = get_scale_image_parameter()
    ret_dict = take_thermal_still(snap_id=snap_id, group_id=group_id, delay=delay, repeat=repeat, scale_image=scale_image)
    return Response(json.dumps(ret_dict), status=202, mimetype='application/json')

@camera.route('/both_still')
def both_still():
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()
    repeat = get_repeat_parameter()

    both_still_dict = both_still_chain(
        snap_id=snap_id,
        group_id=group_id,
        delay=delay,
        repeat=repeat
    )

    return Response(json.dumps(both_still_dict), status=202, mimetype='application/json')

def get_delay_parameter():
    delay = 0
    try:
        if request.args.has_key('delay'):
            delay = int(request.args.get('delay'))
    except ValueError as e:
        pass
    return delay

def get_repeat_parameter():
    repeat = 0
    try:
        if request.args.has_key('repeat'):
            repeat = int(request.args.get('repeat'))
    except ValueError as e:
        pass
    return repeat

def get_scale_image_parameter():
    scale_image = True
    if request.args.has_key('scale_image'):
        scale_image = request.args.get('scale_image')
        # need a cleaner way to parse a boolean from a get parameter.  e.g. 'False' evaluates to True as a non-empty string
    return scale_image
