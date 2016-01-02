import datetime
import json
import os
import sys
import uuid

import cv2
from flask import g, Blueprint, Flask, request, Response, current_app
import numpy as np
import picamera
from pylepton import Lepton

from camera.services import take_picam_still, take_thermal_still
from admin.controller import get_settings_document

camera = Blueprint('camera', __name__)

@camera.route('/')
def index():
    return "Camera"

@camera.route('/picam_still')
def picam_still():
    snap_id = uuid.uuid4()
    pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    task = take_picam_still(snap_id=snap_id, group_id=current_group_id, pic_id=pic_id)
    resp_json = {
        'id': str(pic_id),
        'snap_id': str(snap_id),
        'task_id': str(task.task_id)
    }
    return Response(json.dumps(resp_json), status=202, mimetype='application/json')

@camera.route('/thermal_still')
def thermal_still():
    snap_id = uuid.uuid4()
    pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    task = take_thermal_still(snap_id=snap_id, group_id=current_group_id, pic_id=pic_id)
    resp_json = {
        'id': str(pic_id),
        'snap_id': str(snap_id),
        'task_id': str(task.task_id)
    }
    return Response(json.dumps(resp_json), status=202, mimetype='application/json')

@camera.route('/both_still')
def both_still():
    snap_id = uuid.uuid4()
    thermal_pic_id = uuid.uuid4()
    picam_pic_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    picam_task = take_picam_still(snap_id=snap_id, group_id=current_group_id, pic_id=picam_pic_id)
    thermal_task = take_thermal_still(snap_id=snap_id, group_id=current_group_id, pic_id=thermal_pic_id)
    combo_dict = {
        'picam': {
            'id': str(picam_pic_id),
            'snap_id': str(snap_id),
            'task_id': str(picam_task.task_id)
        }, 
        'thermal': {
            'id': str(thermal_pic_id),
            'snap_id': str(snap_id),
            'task_id': str(thermal_task.task_id)
        }, 
    }
    return Response(json.dumps(combo_dict), status=202, mimetype='application/json')
