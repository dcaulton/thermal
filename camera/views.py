import json
import time
import uuid

from flask import current_app, Blueprint, request, Response, url_for

from admin.services import get_settings_document
from camera.tasks import take_picam_still, take_thermal_still, take_both_still
from thermal.utils import gather_and_enforce_request_args, get_url_base

camera = Blueprint('camera', __name__)


@camera.route('/')
def index():
    '''
    Lists top level endpoints for camera
    '''
    url_base = get_url_base()
    top_level_links = {
        'picam_still': url_base + url_for('camera.picam_still'),
        'thermal_still': url_base + url_for('camera.thermal_still'),
        'both_still': url_base + url_for('camera.both_still'),
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')


@camera.route('/picam_still')
def picam_still():
    '''
    Api endpoint for taking one or a series of Picam stills.
    The still/stills will run asynchronously as Celery tasks, the scheduling work is delegated to the camera.tasks module
    Delaying and Repeating info comes in via GET parameters, the rest comes from the current group record.
    '''
    try:
        snap_id = uuid.uuid4()
        group_id = get_settings_document()['current_group_id']
        # TODO dry this out, we gather delay+repeat three times in this view
        args_dict = gather_and_enforce_request_args([{'name': 'delay', 'default': 0, 'cast_function': int},
                                                     {'name': 'repeat', 'default': 0, 'cast_function': int}])
        delay = args_dict['delay']
        repeat = args_dict['repeat']
        ret_dict = take_picam_still(snap_id=snap_id, group_id=group_id, delay=delay, repeat=repeat)
        return Response(json.dumps(ret_dict), status=202, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@camera.route('/thermal_still')
def thermal_still():
    '''
    Api endpoint for taking one or a series of Lepton stills.
    The still/stills will run asynchronously as Celery tasks, the scheduling work is delegated to the camera.tasks module
    Delaying and Repeating info comes in via GET parameters, the rest comes from the current group record.
    '''
    try:
        snap_id = uuid.uuid4()
        group_id = get_settings_document()['current_group_id']
        args_dict = gather_and_enforce_request_args([{'name': 'delay', 'default': 0, 'cast_function': int},
                                                     {'name': 'repeat', 'default': 0, 'cast_function': int},
                                                     {'name': 'scale_image', 'default': True, 'cast_function': bool}])
        delay = args_dict['delay']
        repeat = args_dict['repeat']
        scale_image = args_dict['scale_image']
        ret_dict = take_thermal_still(snap_id=snap_id, group_id=group_id, delay=delay, repeat=repeat, scale_image=scale_image)
        return Response(json.dumps(ret_dict), status=202, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@camera.route('/both_still')
def both_still():
    '''
    Api endpoint for taking one or a series of 'both' stills - that is, Picam and Lepton stills which are then post-processed
      and merged into a single image
    The still/stills will run asynchronously as Celery tasks, the scheduling work is delegated to the camera.tasks module
    Delaying and Repeating info comes in via GET parameters, the rest comes from the current group record.
    '''
    try:
        snap_id = uuid.uuid4()
        group_id = get_settings_document()['current_group_id']
        args_dict = gather_and_enforce_request_args([{'name': 'delay', 'default': 0, 'cast_function': int},
                                                     {'name': 'repeat', 'default': 0, 'cast_function': int}])
        delay = args_dict['delay']
        repeat = args_dict['repeat']

        both_still_dict = take_both_still(
            snap_id=snap_id,
            group_id=group_id,
            delay=delay,
            repeat=repeat
        )

        return Response(json.dumps(both_still_dict), status=202, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
