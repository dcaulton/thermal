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
    ret_dict = take_picam_still(snap_id=snap_id, group_id=group_id, delay=delay)
    return Response(json.dumps(ret_dict), status=202, mimetype='application/json')

@camera.route('/thermal_still')
def thermal_still():
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()
    scale_image = True
    if request.args.has_key('scale_image'):
        scale_image = request.args.get('scale_image')
        # need a cleaner way to parse a boolean from a get parameter.  e.g. 'False' evaluates to True as a non-empty string
    ret_dict = take_thermal_still(snap_id=snap_id, group_id=group_id, delay=delay, scale_image=scale_image)
    return Response(json.dumps(ret_dict), status=202, mimetype='application/json')

@camera.route('/both_still')
def both_still():
#this doesn't yet use the delay functionality that picam_still and thermal_still methods have
# this isn't aware if the picam takes a second, long exposure that will have a different pid
#   - can be solved if we chain the tasks and have the later tasks look for all pictures associated with this snap
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()

    both_still_dict = both_still_chain(
        snap_id=snap_id,
        group_id=group_id,
        delay=delay
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
