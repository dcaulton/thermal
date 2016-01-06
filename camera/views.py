import json
import time
import uuid

from celery import chain
from flask import Blueprint, request, Response, current_app

from admin.services import get_settings_document
from analysis.services import scale_image, scale_image_chained
from camera.services import take_picam_still, take_thermal_still, take_picam_still_chained
from merging.services import merge_images, merge_images_chained

camera = Blueprint('camera', __name__)

@camera.route('/')
def index():
    return "Camera"

@camera.route('/picam_still')
def picam_still():
# this doesn't capture the potential second picture id if a long exposure is needed
    snap_id = uuid.uuid4()
    pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    delay = 0
    if request.args.has_key('delay'):
        delay = int(request.args.get('delay'))
    task = take_picam_still.apply_async(
        kwargs={
            'snap_id': snap_id,
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
    pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    delay = 0
    if request.args.has_key('delay'):
        delay = int(request.args.get('delay'))
    task = take_thermal_still.apply_async(
        kwargs={
            'snap_id': snap_id,
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
    time.sleep(1)
    scaled_image_id = uuid.uuid4()
    scale_image(img_id_in=pic_id, img_id_out=scaled_image_id)
    return Response(json.dumps(resp_json), status=202, mimetype='application/json')

@camera.route('/both_still')
def both_still():
#this doesn't yet use the delay functionality that picam_still and thermal_still methods have
# this isn't aware if the picam takes a second, long exposure that will have a different pid
#   - can be solved if we chain the tasks and have the later tasks look for all pictures associated with this snap
    snap_id = uuid.uuid4()
    thermal_pic_id = uuid.uuid4()
    picam_pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']

    scaled_pic_id = uuid.uuid4()
    merged_pic_id = uuid.uuid4()

    chain(
        take_thermal_still.s(
            snap_id=snap_id,
            group_id=current_group_id,
            pic_id=thermal_pic_id
        ),
        take_picam_still_chained.s(
            snap_id=snap_id,
            group_id=current_group_id,
            pic_id=picam_pic_id
        ),
        scale_image_chained.s(
            img_id_in=thermal_pic_id,
            img_id_out=scaled_pic_id
        ),
        merge_images_chained.s(
            img1_id_in=picam_pic_id,
            img2_id_in=scaled_pic_id,
            img_id_out=merged_pic_id
        )
    ).apply_async()

    combo_dict = {
        'snap_id': str(snap_id),
        'picam_id': str(picam_pic_id),
        'thermal_id': str(thermal_pic_id),
        'scaled_id': str(scaled_pic_id),
        'merged_id': str(merged_pic_id)
    }
    return Response(json.dumps(combo_dict), status=202, mimetype='application/json')
