import json

from flask import Blueprint, Response

from thermal.utils import get_document_with_exception
from thermal.views import generic_get_view, generic_list_view


picture = Blueprint('picture', __name__)


@picture.route('/')
def list_pictures():
    '''
    Lists all pictures
    Supports paging and filtering on any picture attribute via get parms
    '''
    return generic_list_view(document_type='picture')


@picture.route('/<picture_id>')
def get_picture(picture_id):
    '''
    Retrieves a picture for the supplied id
    '''
    return generic_get_view(item_id=picture_id, document_type='picture')
