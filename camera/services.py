import datetime
import os
import uuid

import cv2
from flask import current_app, g
import numpy as np
import picamera
from pylepton import Lepton

from thermal.appmodule import celery

@celery.task
def take_picam_still(snap_id, group_id, pic_id, picture_name):
    with picamera.PiCamera() as camera:
        pic_path = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], picture_name)
        camera.resolution = (current_app.config['STILL_IMAGE_WIDTH'], current_app.config['STILL_IMAGE_HEIGHT'])
        camera.capture(pic_path)
        pic_dict = {
            'type': 'picture',
            'camera_type': 'picam',
            'group_id': str(group_id),
            'snap_id': str(snap_id),
            'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path),
            'created': str(datetime.datetime.now())
        }
        current_app.db[str(pic_id)] = pic_dict


@celery.task
def take_thermal_still(snap_id, group_id, pic_id, picture_name):
    with Lepton("/dev/spidev0.1") as l:
        a,_ = l.capture()
        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(a, 8, a)
        pic_path = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], picture_name)
        cv2.imwrite(pic_path, np.uint8(a))
        pic_dict = {
            'type': 'picture',
            'camera_type': 'thermal',
            'group_id': str(group_id),
            'snap_id': str(snap_id),
            'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path),
            'created': str(datetime.datetime.now())
        }
        current_app.db[str(pic_id)] = pic_dict
