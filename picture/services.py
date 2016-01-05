from flask import current_app

from thermal.exceptions import NotFoundError
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
