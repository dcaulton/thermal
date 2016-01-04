import datetime
from fractions import Fraction
import io
import os
from time import sleep
import uuid

import cv2
from flask import current_app, g
import numpy as np
import picamera
from PIL import Image, ImageStat
from pylepton import Lepton

from thermal.appmodule import celery

def get_brightness(filename):
    image = Image.open(filename).convert('L')
    stat = ImageStat.Stat(image)
    avg_pixel_value = stat.mean[0]
    print "picam image brightness is {0}".format(avg_pixel_value)
    return avg_pixel_value

def take_standard_exposure_picam_still(pic_path):
    with picamera.PiCamera() as camera:
        camera.resolution = (current_app.config['STILL_IMAGE_WIDTH'], current_app.config['STILL_IMAGE_HEIGHT'])
        camera.capture(pic_path)

def take_long_exposure_picam_still(pic_path):
#TODO: tune this to adjust exposure length based on brightness from the standard exposure picam image that was just taken
    print 'taking long exposure'
    with picamera.PiCamera() as camera:
        camera.resolution = (current_app.config['STILL_IMAGE_WIDTH'], current_app.config['STILL_IMAGE_HEIGHT'])
        # Set a framerate of 1/6fps, then set shutter
        # speed to 6s and ISO to 800
        camera.framerate = Fraction(1, 6)
        camera.shutter_speed = 6000000
        camera.exposure_mode = 'off'
        camera.iso = 800
        # Give the camera a good long time to measure AWB
        # (you may wish to use fixed AWB instead)
        sleep(2)
        # Finally, capture an image with a 6s exposure. Due
        # to mode switching on the still port, this will take
        # longer than 6 seconds
        camera.capture(pic_path)

@celery.task
def take_picam_still(snap_id, group_id, pic_id):
    picture_name = "{0}.jpg".format(pic_id)
    pic_path = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], picture_name)
    pic_dict = {
        'type': 'picture',
        'camera_type': 'picam',
        'exposure_type': 'standard',
        'group_id': str(group_id),
        'snap_id': str(snap_id),
        'filename': picture_name,
        'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path),
        'created': str(datetime.datetime.now())
    }
    take_standard_exposure_picam_still(pic_path)
    current_app.db[str(pic_id)] = pic_dict
    brightness = get_brightness(pic_path)
    if brightness < 5.0:
        long_exposure_pic_id = uuid.uuid4()
        picture_name = "{0}.jpg".format(long_exposure_pic_id)
        pic_path = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], picture_name)
        pic_dict['exposure_type'] = 'long'
        take_long_exposure_picam_still(pic_path)
        current_app.db[str(pic_id)] = pic_dict


@celery.task
def take_thermal_still(snap_id, group_id, pic_id):
    picture_name = "{0}.jpg".format(pic_id)
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
            'filename': picture_name,
            'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path),
            'created': str(datetime.datetime.now())
        }
        current_app.db[str(pic_id)] = pic_dict
