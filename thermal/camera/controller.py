import cv2
import datetime
from flask import g, Blueprint, Flask, request, Response, current_app
import json
import numpy as np
import os
import picamera
from pylepton import Lepton
import sys
import uuid


camera = Blueprint('camera', __name__)

current_group_id = uuid.uuid4()

@camera.route('/')
def index():
    return "Camera"

@camera.route('/picam_still')
def picam_still():
    snap_uuid=uuid.uuid4()
    (resp_json,resp_code) = take_picam_still(snap_uuid)
    return Response(json.dumps(resp_json), status=resp_code, mimetype='application/json')

def take_picam_still(snap_uuid):
    with picamera.PiCamera() as camera:
        pic_path = os.path.join('/home/pi', 'Pictures', str(snap_uuid)+'-picam.jpg')
        camera.capture(pic_path)
        pic_dict = {'type': 'picture',
                    'camera_type': 'picam',
                    'group_id': str(current_group_id),
                    'snap_id': str(snap_uuid),
                    'uri': 'file://strangefruit4'+pic_path,
                    'created': str(datetime.datetime.now())
                   }
        save_uuid=uuid.uuid4()
        g.db[str(save_uuid)] = pic_dict
        return (pic_dict,200)

@camera.route('/thermal_still')
def thermal_still():
    snap_uuid=uuid.uuid4()
    (resp_json,resp_code) = take_thermal_still(snap_uuid)
    return Response(json.dumps(resp_json), status=resp_code, mimetype='application/json')

def take_thermal_still(snap_uuid):
    try:
        with Lepton("/dev/spidev0.1") as l:
            a,_ = l.capture()
            cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
            np.right_shift(a, 8, a)
            pic_path = os.path.join('/home/pi', 'Pictures', str(snap_uuid)+'-thermal.jpg')
            cv2.imwrite(pic_path, np.uint8(a))
            pic_dict = {'type': 'picture',
                        'camera_type': 'thermal',
                        'group_id': str(current_group_id),
                        'snap_id': str(snap_uuid),
                        'uri': 'file://strangefruit4'+pic_path,
                        'created': str(datetime.datetime.now())
                       }
            save_uuid=uuid.uuid4()
            g.db[str(save_uuid)] = pic_dict
            return (pic_dict,200)
    except Exception as e:
        e = sys.exc_info()[0]
        return (e,200)

@camera.route('/both_still')
def both_still():
    snap_uuid=uuid.uuid4()
    picam_dict = take_picam_still(snap_uuid)[0]
    thermal_dict = take_thermal_still(snap_uuid)[0]
    combo_dict={'picam': picam_dict, 'thermal': thermal_dict}
    return Response(json.dumps(combo_dict), status=200, mimetype='application/json')
