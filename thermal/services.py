import os

from flask import current_app, request

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
    if request is not None and 'args' in dir(request): # only gather parms if we have a request context
        the_dict = gather_and_enforce_request_args(['ANY_SEARCHABLE'])
        for key in the_dict:
            args_dict[key] = the_dict[key]
    args_dict['type'] = document_type
    documents_dict = get_documents_from_criteria(args_dict)
    return documents_dict


def get_generic(item_id, document_type):
    if not item_exists(item_id, document_type):
        raise NotFoundError("{0} not found for id {1}".format(document_type, item_id))
    item_dict = get_document(item_id)
    return item_dict


def update_generic(document_in, document_type):
    '''
    requires document to have at least _id and type
    '''
    if '_id' in document_in:
        the_id = cast_uuid_to_string(document_in['_id'])
        if not item_exists(the_id, 'any'):
            raise DocumentConfigurationError('trying to update {0} when no document exists for that id'.format(the_id))
        if not item_exists(the_id, document_type):
            raise DocumentConfigurationError('trying to alter document type for id {0} during update'.format(the_id))
        save_document(document_in)
    else:
         raise DocumentConfigurationError('trying to update a document with no id')

def save_generic(document_in, document_type):  # a wrapper function just to have consistent naming and function location
    '''
    requires document to have at least _id and type
    '''
    if '_id' in document_in:
        if 'type' not in document_in:
             raise DocumentConfigurationError('trying to save the document with no value for type')
        if document_in['type'] != document_type:
             raise DocumentConfigurationError('trying to save the document that is not of type {0}'.format(str(document_type)))
        save_document(document_in)
    else:
         raise DocumentConfigurationError('trying to save a document with no id')
