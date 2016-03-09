import uuid

from flask import current_app, url_for

from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import (get_documents_from_criteria,
                           get_document,
                           item_exists,
                           save_document)

def find_distortion_sets(args_dict):
    args_dict['type'] = 'distortion_set'
    distortion_sets_dict = get_documents_from_criteria(args_dict)
    return distortion_sets_dict

def get_distortion_set_document(distortion_set_id):
    if not item_exists(distortion_set_id, 'distortion_set'):
        raise NotFoundError("distortion set not found for id {0}".format(distortion_set_id))
    distortion_set_dict = get_document(distortion_set_id)
    return distortion_set_dict

def find_distortion_pairs(args_dict):
    args_dict['type'] = 'distortion_pair'
    distortion_pairs_dict = get_documents_from_criteria(args_dict)
    return distortion_pairs_dict

def get_distortion_pair_document(distortion_pair_id):
    if not item_exists(distortion_pair_id, 'distortion_pair'):
        raise NotFoundError("distortion pair not found for id {0}".format(distortion_pair_id))
    distortion_pair_dict = get_document(distortion_pair_id)
    return distortion_pair_dict

def find_calibration_sessions(args_dict):
    args_dict['type'] = 'calibration_session'
    calibration_sessions_dict = get_documents_from_criteria(args_dict)
    return calibration_sessions_dict

def get_calibration_session_document(calibration_session_id):
    if not item_exists(calibration_session_id, 'calibration_session'):
        raise NotFoundError("calibration session not found for id {0}".format(calibration_session_id))
    calibration_session_dict = get_document(calibration_session_id)
    return calibration_session_dict
