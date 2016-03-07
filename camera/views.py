import json
import time
import uuid

from flask import current_app, Blueprint, request, Response, url_for

from admin.services import get_settings_document
from camera.tasks import take_picam_still, take_thermal_still, take_both_still, take_both_still_test
from thermal.utils import _get_parameter, get_url_base

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
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()
    repeat = get_repeat_parameter()
    ret_dict = take_picam_still(snap_id=snap_id, group_id=group_id, delay=delay, repeat=repeat)
    return Response(json.dumps(ret_dict), status=202, mimetype='application/json')


@camera.route('/thermal_still')
def thermal_still():
    '''
    Api endpoint for taking one or a series of Lepton stills.
    The still/stills will run asynchronously as Celery tasks, the scheduling work is delegated to the camera.tasks module
    Delaying and Repeating info comes in via GET parameters, the rest comes from the current group record.
    '''
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()
    repeat = get_repeat_parameter()
    scale_image = get_scale_image_parameter()
    ret_dict = take_thermal_still(snap_id=snap_id, group_id=group_id, delay=delay, repeat=repeat, scale_image=scale_image)
    return Response(json.dumps(ret_dict), status=202, mimetype='application/json')


@camera.route('/both_still')
def both_still():
    '''
    Api endpoint for taking one or a series of 'both' stills - that is, Picam and Lepton stills which are then post-processed
      and merged into a single image
    The still/stills will run asynchronously as Celery tasks, the scheduling work is delegated to the camera.tasks module
    Delaying and Repeating info comes in via GET parameters, the rest comes from the current group record.
    '''
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()
    repeat = get_repeat_parameter()

    both_still_dict = take_both_still(
        snap_id=snap_id,
        group_id=group_id,
        delay=delay,
        repeat=repeat
    )

    return Response(json.dumps(both_still_dict), status=202, mimetype='application/json')


@camera.route('/both_still_test')
def both_still_test():
    '''
    for experimental both_still
    '''
    snap_id = uuid.uuid4()
    group_id = get_settings_document()['current_group_id']
    delay = get_delay_parameter()
    repeat = get_repeat_parameter()

    both_still_dict = take_both_still_test(
        snap_id=snap_id,
        group_id=group_id,
        delay=delay,
        repeat=repeat
    )

    return Response(json.dumps(both_still_dict), status=202, mimetype='application/json')


def get_delay_parameter():
    '''
    Extracts the delay parameter from the GET parameters.
    Has a hardcoded default of 'shoot immediately'
    '''
    return _get_parameter('delay', default=0, cast_function=int)


def get_repeat_parameter():
    '''
    Extracts the repeat parameter from the GET parameters.
    Has a hardcoded default of 'one picture only, no repeating behavior'
    '''
    return _get_parameter('repeat', default=0, cast_function=int)


def get_scale_image_parameter():
    '''
    Extracts a parameter from the GET parameters which indicates if the user wants the Lepton image, which will be coming in
      as 80x60, to be scaled up and colorized
    Has a hardcoded default of 'yes, scale and colorize it up'
    So you have to pass it something like 0 or '' to suppress
    '''
    return _get_parameter('scale_image', default=True, cast_function=bool)
