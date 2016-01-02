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

from admin.controller import get_settings_document

camera = Blueprint('camera', __name__)

@camera.route('/')
def index():
    return "Camera"

@camera.route('/picam_still')
def picam_still():
    current_group_id = get_settings_document()['current_group_id']
    (resp_json,resp_code) = take_picam_still(snap_id=uuid.uuid4(), group_id=current_group_id)
    return Response(json.dumps(resp_json), status=resp_code, mimetype='application/json')

def take_picam_still(snap_id, group_id):
    with picamera.PiCamera() as camera:
        pic_path = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], "{0}-p.jpg".format(snap_id))
        camera.capture(pic_path)
        pic_dict = {'type': 'picture',
                    'camera_type': 'picam',
                    'group_id': str(group_id),
                    'snap_id': str(snap_id),
                    'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path),
                    'created': str(datetime.datetime.now())
                   }
        save_uuid=uuid.uuid4()
        g.db[str(save_uuid)] = pic_dict
        return (pic_dict, 201)

@camera.route('/thermal_still')
def thermal_still():
    snap_id = uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    (resp_json,resp_code) = take_thermal_still(snap_id=snap_id, group_id=current_group_id)
    return Response(json.dumps(resp_json), status=resp_code, mimetype='application/json')

def take_thermal_still(snap_id, group_id):
    try:
        with Lepton("/dev/spidev0.1") as l:
            a,_ = l.capture()
            cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
            np.right_shift(a, 8, a)
            pic_path = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], "{0}-t.jpg".format(snap_id))
            cv2.imwrite(pic_path, np.uint8(a))
            pic_dict = {'type': 'picture',
                        'camera_type': 'thermal',
                        'group_id': str(group_id),
                        'snap_id': str(snap_id),
                        'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path),
                        'created': str(datetime.datetime.now())
                       }
            save_uuid=uuid.uuid4()
            g.db[str(save_uuid)] = pic_dict
            return (pic_dict, 201)
    except Exception as e:
        e = sys.exc_info()[0]
        return (e,400)

@camera.route('/both_still')
def both_still():
    snap_id=uuid.uuid4()
    current_group_id = get_settings_document()['current_group_id']
    picam_dict = take_picam_still(snap_id=snap_id, group_id=current_group_id)[0]
    thermal_dict = take_thermal_still(snap_id=snap_id, group_id=current_group_id)[0]
    combo_dict={'picam': picam_dict, 'thermal': thermal_dict}
    return Response(json.dumps(combo_dict), status=201, mimetype='application/json')
