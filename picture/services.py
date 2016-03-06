import os

from flask import current_app

from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import (cast_uuid_to_string,
                           get_document,
                           get_documents_from_criteria,
                           item_exists,
                           save_document)


def find_pictures(args_dict, **kwargs):
    '''
    Finds all pictures matching the parameters passed in with the kwargs dict
    It's just a think wrapper around get_documents_from_criteria
    '''
    args_dict['type'] = 'picture'
    pictures_dict = get_documents_from_criteria(args_dict, **kwargs)
    return pictures_dict


def find_picture(picture_id):
    picture_id = str(picture_id)
    if not item_exists(picture_id, 'picture'):
        raise NotFoundError("picture not found for id {0}".format(picture_id))
    picture_dict = get_document(picture_id)
    return picture_dict


def save_picture_document(the_dict):
    if '_id' not in the_dict:
        the_dict['_id'] == cast_uuid_to_string(uuid.uuid4())
    the_id = the_dict['_id']
    if item_exists(the_id, 'any'):
        raise DocumentConfigurationError('trying to save the pic with a preexisting id: {0}'.format(str(the_id)))
    if 'type' in the_dict and the_dict['type'] != 'picture':
        raise DocumentConfigurationError('trying to save as a picture a document that is not of type picture: {0}'\
                                         .format(str(the_id)))
    else:
        save_document(the_dict)


def update_picture_document(the_dict):
    the_id = the_dict['_id']
    if not item_exists(the_id, 'picture'):
        raise DocumentConfigurationError('trying to update a picture when no picture exists for that id: {0}'.format(str(the_id)))
    else:
        save_document(the_dict)


def build_picture_path(picture_name, snap_id='', create_directory=True):
    pictures_directory = current_app.config['PICTURE_SAVE_DIRECTORY']
    temp_directory = os.path.join(pictures_directory, str(snap_id))
    if create_directory and not os.path.isdir(temp_directory):
        os.mkdir(temp_directory)
    return os.path.join(temp_directory, picture_name)


def build_picture_name(pic_id):
    return "{0}.jpg".format(pic_id)
