import json
import uuid

from flask import Blueprint, request, Response, current_app

from camera.services import take_picam_still, take_thermal_still
from admin.services import get_settings_document

camera = Blueprint('camera', __name__)

@camera.route('/')
def index():
    return "Camera"

@camera.route('/picam_still')
def picam_still():
    snap_id = uuid.uuid4()
    picture_name = "{0}-p.jpg".format(snap_id)
    pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    delay = 0
    if request.args.has_key('delay'):
        delay = int(request.args.get('delay'))
    task = take_picam_still.apply_async(
        kwargs={
            'snap_id': snap_id,
            'picture_name': picture_name,
            'group_id': current_group_id, 
            'pic_id': pic_id
        },
        countdown=delay
    )
    resp_json = {
        'id': str(pic_id),
        'task_id': task.task_id,
        'snap_id': str(snap_id)
    }
    return Response(json.dumps(resp_json), status=202, mimetype='application/json')

@camera.route('/thermal_still')
def thermal_still():
    snap_id = uuid.uuid4()
    picture_name = "{0}-t.jpg".format(snap_id)
    pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    delay = 0
    if request.args.has_key('delay'):
        delay = int(request.args.get('delay'))
    task = take_thermal_still.apply_async(
        kwargs={
            'snap_id': snap_id,
            'picture_name': picture_name,
            'group_id': current_group_id, 
            'pic_id': pic_id
        },
        countdown=delay
    )
    resp_json = {
        'id': str(pic_id),
        'task_id': task.task_id,
        'snap_id': str(snap_id)
    }
    return Response(json.dumps(resp_json), status=202, mimetype='application/json')

@camera.route('/both_still')
def both_still():
    snap_id = uuid.uuid4()
    picam_picture_name = "{0}-p.jpg".format(snap_id)
    thermal_picture_name = "{0}-t.jpg".format(snap_id)
    thermal_pic_id = uuid.uuid4()
    picam_pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    take_picam_still.delay(
        snap_id=snap_id,
        picture_name=picam_picture_name,
        group_id=current_group_id,
        pic_id=picam_pic_id
    )
    take_thermal_still.delay(
        snap_id=snap_id,
        picture_name=thermal_picture_name,
        group_id=current_group_id,
        pic_id=thermal_pic_id
    )
    combo_dict = {
        'picam': {
            'id': str(picam_pic_id),
            'snap_id': str(snap_id)
        }, 
        'thermal': {
            'id': str(thermal_pic_id),
            'snap_id': str(snap_id)
        }, 
    }
    return Response(json.dumps(combo_dict), status=202, mimetype='application/json')
