import uuid

from flask import current_app, url_for

from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import (get_documents_from_criteria,
                           get_document_with_exception,
                           item_exists,
                           save_document)

def find_distortion_sets(args_dict):
    args_dict['type'] = 'distortion_set'
    distortion_sets_dict = get_documents_from_criteria(args_dict)
    return distortion_sets_dict

def get_distortion_set_document(distortion_set_id):
    distortion_set_dict = get_document_with_exception(distortion_set_id, document_type='distortion_set')
    return distortion_set_dict

def find_distortion_pairs(args_dict):
    args_dict['type'] = 'distortion_pair'
    distortion_pairs_dict = get_documents_from_criteria(args_dict)
    return distortion_pairs_dict

def get_distortion_pair_document(distortion_pair_id):
    distortion_pair_dict = get_document_with_exception(distortion_pair_id, document_type='distortion_pair')
    return distortion_pair_dict

def find_calibration_sessions(args_dict):
    args_dict['type'] = 'calibration_session'
    calibration_sessions_dict = get_documents_from_criteria(args_dict)
    return calibration_sessions_dict

def get_calibration_session_document(calibration_session_id):
    calibration_session_dict = get_document_with_exception(calibration_session_id, document_type='calibration_session')
    return calibration_session_dict
