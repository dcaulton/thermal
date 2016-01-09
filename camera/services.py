import datetime
import io
import os
import uuid

from flask import current_app

from admin.services import get_group_document
from analysis.services import check_if_image_is_too_dark
from cameras import Lepton, Picam

def take_standard_exposure_picam_still(pic_path):
    '''
    Used to interface with the Picam camera to take a standard, or automatically exposed image
    '''
    picam = Picam()
    picam.take_still(
        pic_path=pic_path,
        image_width=current_app.config['STILL_IMAGE_WIDTH'],
        image_height=current_app.config['STILL_IMAGE_HEIGHT']
    )

def take_long_exposure_picam_still(pic_path):
    '''
    Used to take a generic 'long exposure image' from the Picam camera if earlier logic determines that conditions warrant
    It's currently configured to always take what seems to be the longest possible exposure
    '''
#TODO: tune this to adjust exposure length based on brightness from the standard exposure picam image that was just taken
    print 'taking long exposure'
    picam = Picam()
    picam.take_long_exposure_still(
        pic_path=pic_path,
        image_width=current_app.config['STILL_IMAGE_WIDTH'],
        image_height=current_app.config['STILL_IMAGE_HEIGHT']
    )

def get_retake_picam_pics_when_dark_setting(group_document):
    '''
    Handles getting a setting from the group document intended to reflect if a user wants to retake picam photos
      during this session if they are too dim.  It's not a decision to be taken lightly, long exposures can 
      take around 50 seconds and definitely affect ones workflow.
    Has a hardcoded default value of False
    '''
    if 'retake_picam_pics_when_dark' in group_document.keys():
        return group_document['retake_picam_pics_when_dark']
    return False

def get_brightness_threshold(group_document):
    '''
    Handles getting a 'brightness threshold' value from the supplied group document.
    Has a hard coded default, forces the value to be a float.
    This information is used by the analysis service to determine if some particular picture meets a user-defined
      limit for being too dark
    '''
    try:
        if 'picam_brightness_threshold' in group_document.keys():
            return float(group_document['picam_brightness_threshold'])
    except ValueError as e:
        pass
    return 5.0

def take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id):
    '''
    Top level method in the camera service for taking a still image via the picam (regular raspberry pi) camera.
    Also saves a picture record to the db
    Depending on settings and real time conditions, may cause a second, longer exposure to be taken
    '''
    group_document = get_group_document(str(group_id))
    retake_picam_pics_when_dark = get_retake_picam_pics_when_dark_setting(group_document)
    brightness_threshold = get_brightness_threshold(group_document)

    picture_name = build_picture_name(normal_exposure_pic_id)
    pic_path = build_pic_path(picture_name)
    pic_dict = {
        'type': 'picture',
        'source': 'picam',
        'exposure_type': 'standard',
        'group_id': str(group_id),
        'snap_id': str(snap_id),
        'filename': picture_name,
        'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path),
        'created': str(datetime.datetime.now())
    }
    take_standard_exposure_picam_still(pic_path)
    current_app.db[str(normal_exposure_pic_id)] = pic_dict
    image_is_too_dark = check_if_image_is_too_dark(pic_path, brightness_threshold)
    if image_is_too_dark and retake_picam_pics_when_dark:
        picture_name = build_picture_name(long_exposure_pic_id)
        pic_path = build_pic_path(picture_name)
        pic_dict['exposure_type'] = 'long'
        pic_dict['filename'] = picture_name
        pic_dict['uri'] = "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path)
        pic_dict['created'] = str(datetime.datetime.now())
        take_long_exposure_picam_still(pic_path)
        current_app.db[str(long_exposure_pic_id)] = pic_dict

def build_pic_path(picture_name):
    return os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], picture_name)

def build_picture_name(pic_id):
    return "{0}.jpg".format(pic_id)

def take_thermal_still(snap_id, group_id, pic_id):
    '''
    Top level method in the camera service for taking a still image via the Lepton camera.
    Also saves a picture record to the db
    '''
    picture_name = build_picture_name(pic_id)
    pic_path = build_pic_path(picture_name)
    lepton = Lepton()
    lepton.take_still(pic_path=pic_path)

    pic_dict = {
        'type': 'picture',
        'source': 'thermal',
        'group_id': str(group_id),
        'snap_id': str(snap_id),
        'filename': picture_name,
        'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path),
        'created': str(datetime.datetime.now())
    }
    current_app.db[str(pic_id)] = pic_dict
