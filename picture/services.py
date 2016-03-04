import os

from flask import current_app

from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import get_documents_from_criteria, save_document


def find_pictures(args_dict, **kwargs):
    args_dict['type'] = 'picture'
    pictures_dict = get_documents_from_criteria(args_dict, **kwargs)
    return pictures_dict


def find_picture(picture_id):
    picture_id = str(picture_id)  # deal with non-stringified UUIDs coming in
    if picture_id in current_app.db:
        picture_dict = current_app.db[picture_id]
    else:
        raise NotFoundError("picture not found for id {0}".format(picture_id))
    return picture_dict


def save_picture_document(the_dict):
    the_id = the_dict['_id']
    if the_id in current_app.db:
        raise DocumentConfigurationError('trying to save the pic with a preexisting id: {0}'.format(str(the_id)))
    if 'type' not in the_dict.keys():
        raise DocumentConfigurationError('trying to save the pic with no value for type: {0}'.format(str(the_id)))
    if the_dict['type'] != 'picture':
        raise DocumentConfigurationError('trying to save as a picture a document that is not of type picture: {0}'.format(str(the_id)))
    else:
        current_app.db[the_id] = the_dict


def update_picture_document(the_dict):
    the_id = the_dict['_id']
    if the_id not in current_app.db:
        raise DocumentConfigurationError('trying to update a pic whose id isnt in the db: {0}'.format(str(the_id)))
    if 'type' not in the_dict.keys():
        raise DocumentConfigurationError('trying to save the pic with no value for type: {0}'.format(str(the_id)))
    if the_dict['type'] != 'picture':
        raise DocumentConfigurationError('trying to save as a picture a document that is not of type picture: {0}'.format(str(the_id)))
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
