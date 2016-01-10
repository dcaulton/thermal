from flask import current_app

from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import get_documents_from_criteria

def find_pictures(args_dict):
    args_dict = dict((key, args_dict.getlist(key)[0]) for key in args_dict.keys())
    args_dict['type'] = 'picture'
    pictures_dict = get_documents_from_criteria(args_dict=args_dict)
    return pictures_dict
    
def find_picture(picture_id):
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
