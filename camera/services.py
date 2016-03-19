import copy
import datetime
import io
import os
import uuid

from flask import current_app

from admin.services import get_group_document
from analysis.services import check_if_image_is_too_dark
from cameras import Lepton, Picam
from picture.services import build_picture_path, build_picture_name
from thermal.exceptions import DocumentConfigurationError
from thermal.utils import item_exists
from thermal.services import save_generic


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
# TODO tune this to adjust exposure length based on brightness from the standard exposure picam image that was just taken
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


# TODO make these kwargs, not positional args
def take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id, clean_up_files=True):
    '''
    Top level method in the camera service for taking a still image via the picam (regular raspberry pi) camera.
    Also saves a picture record to the db
    Depending on settings and real time conditions, may cause a second, longer exposure to be taken
    '''
    group_document = get_group_document(str(group_id))
    retake_picam_pics_when_dark = get_retake_picam_pics_when_dark_setting(group_document)
    brightness_threshold = get_brightness_threshold(group_document)

    picture_name = build_picture_name(normal_exposure_pic_id)
    pic_path = build_picture_path(picture_name=picture_name, snap_id=snap_id)
    pic_dict = {
        '_id': str(normal_exposure_pic_id),
        'type': 'picture',
        'source': 'picam',
        'exposure_type': 'standard',
        'group_id': str(group_id),
        'snap_id': str(snap_id),
        'filename': picture_name,
        'uri': pic_path,
        'created': str(datetime.datetime.now())
    }
    take_standard_exposure_picam_still(pic_path)
    save_picture(pic_dict, clean_up_files=clean_up_files)
    image_is_too_dark = check_if_image_is_too_dark(pic_path, brightness_threshold)
    if image_is_too_dark and retake_picam_pics_when_dark:
        picture_name = build_picture_name(long_exposure_pic_id)
        pic_path = build_picture_path(picture_name=picture_name, snap_id=snap_id)
        pic_dict2 = copy.deepcopy(pic_dict)
        pic_dict2['exposure_type'] = 'long'
        pic_dict2['_id'] = str(long_exposure_pic_id)
        pic_dict2['filename'] = picture_name
        pic_dict2['uri'] = pic_path
        pic_dict2['created'] = str(datetime.datetime.now())
        take_long_exposure_picam_still(pic_path)
        save_picture(pic_dict2)  # no need to pass clean_up_files, it's been built into the snap record with the standard exp pic


def take_thermal_still(snap_id, group_id, pic_id, clean_up_files=True):
    '''
    Top level method in the camera service for taking a still image via the Lepton camera.
    Also saves a picture record to the db
    '''
    picture_name = build_picture_name(pic_id)
    pic_path = build_picture_path(picture_name=picture_name, snap_id=snap_id)
    lepton = Lepton()
    lepton.take_still(pic_path=pic_path)

    pic_dict = {
        '_id': str(pic_id),
        'type': 'picture',
        'source': 'thermal',
        'group_id': str(group_id),
        'snap_id': str(snap_id),
        'filename': picture_name,
        'uri': pic_path,
        'created': str(datetime.datetime.now())
    }
    save_picture(pic_dict, clean_up_files=clean_up_files)


def save_picture(pic_dict, clean_up_files=True):
    '''
    Saves the incoming pic_dict as a record of type picture
    If no snap record exists yet for pic_dict['snap_id'], one is created with the supplied value for clean_up_files
    '''
    if 'snap_id' not in pic_dict:
        raise DocumentConfigurationError('no snap_id specified for id {0}'.format(str(group_id)))
    if not item_exists(pic_dict['snap_id'], 'snap'):
        snap_dict = {'_id': pic_dict['snap_id'],
                     'type': 'snap',
                     'clean_up_files': clean_up_files}
        save_generic(snap_dict, 'snap')
    save_generic(pic_dict, 'picture')
