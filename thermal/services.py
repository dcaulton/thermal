import os

from flask import current_app

from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import (cast_uuid_to_string,
                           gather_and_enforce_request_args,
                           get_document,
                           get_documents_from_criteria,
                           item_exists,
                           save_document)


def search_generic(document_type='', args_dict={}):
    '''
    Finds all documents of the specified type matching the parameters passed in with the wargs dict
    It's just a wrapper around get_documents_from_criteria
    THIS CAN THROW EXCEPTIONS, it needs to run within a try except block
    '''
    the_dict = gather_and_enforce_request_args(['ANY_SEARCHABLE'])
    for key in the_dict:
        args_dict[key] = the_dict[key]
    args_dict['type'] = document_type
    documents_dict = get_documents_from_criteria(args_dict)
    return documents_dict


def get_generic(item_id, document_type):
    if not item_exists(item_id, document_tupe):
        raise NotFoundError("{0} not found for id {1}".format(document_type, item_id))
    item_dict = get_document(item_id)
    return item_doct


def update_generic_document(the_dict, document_type):
    the_id = the_dict['_id']
    if not item_exists(the_id, document_type):
        raise DocumentConfigurationError('trying to update a {0} when no {1} exists for that id: {2}'.format(document_type,
                                                                                                             document_type,
                                                                                                             str(the_id)))
    else:
        save_document(the_dict)
