import __builtin__
from collections import OrderedDict

from flask import current_app, request

from thermal.exceptions import DocumentConfigurationError, NotFoundError


dynamically_calculated_attributes = ['current_group_link', 'picture_links', 'snap_list']


def get_documents_from_criteria(args_dict, **kwargs):
    '''
    Takes key value pairs in an args dict and does a query against the database, testing for equality on all pairs.
    Also supports a few special kwargs to handle things like testing for a key not being null, or paging
    '''
    # TODO have this add virtual properties
    documents_dict = {}
    criteria_list = []
    if 'gallery_url_not_null' in args_dict:
        criteria_list.append("doc.gallery_url != null")
        del args_dict['gallery_url_not_null']
    (paging_requested, start_index, end_index) = get_paging_info(**kwargs)

    for key in args_dict:
        criteria_list.append("doc.{0} == '{1}'".format(key, args_dict[key]))
    criteria_string = ' && '.join(criteria_list)
    map_fun = "function(doc) {{if ("
    map_fun = map_fun + criteria_string
    map_fun = map_fun + ") {{emit(doc.created, doc);}}}}"
    for (row_number, row) in enumerate(current_app.db.query(map_fun).rows):
        if paging_requested:
            if row_number >= start_index and row_number <= end_index:
                documents_dict[row['value']['_id']] = row['value']
        else:
            documents_dict[row['value']['_id']] = row['value']
    return documents_dict


def get_paging_info(**kwargs):
    paging_requested = False
    start_index = 0
    end_index = 0
    if 'page_number' in kwargs and kwargs['page_number'] and 'items_per_page' in kwargs and kwargs['items_per_page']:
        try:
            items_per_page = int(kwargs['items_per_page'])
        except ValueError as e:
            raise DocumentConfigurationError('invalid number specified for items_per_page: {0}'.format(kwargs['items_per_page']))
        try:
            page_number = int(kwargs['page_number'])
        except ValueError as e:
            raise DocumentConfigurationError('invalid number specified for page_number: {0}'.format(kwargs['page_number']))
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page - 1
        if page_number < 1:
            raise DocumentConfigurationError('page_number must be a number greater than zero')
        if items_per_page < 1:
            raise DocumentConfigurationError('items_per_page must be a number greater than zero')
        paging_requested = True
    return (paging_requested, start_index, end_index)

def get_url_base():
    '''
    Builds a base url for this application, including scheme and host/port
    '''
    return request.environ['wsgi.url_scheme'] + '://' + request.environ['HTTP_HOST']

def item_exists(item_id, item_type='any'):
    '''
    Checks if an item exists in the db for the supplied item_id and item_type.  Returns True if it exists, False otherwise
    If item_type is supplied as 'any', then it returns True if any document exists with that id, False otherwise.
    '''
    item_id = cast_uuid_to_string(item_id)
    if item_id and item_id in current_app.db:
        if item_type == 'any':
            return True
        else:
            item_dict = current_app.db[item_id]
            if item_dict['type'] == item_type:
                return True
    return False

def doc_attribute_can_be_set(key_name):
    '''
    Checks if a supplied key name can be saved with a document to the database.
    Not record-specific, we don't really have models with this application
    '''
    if key_name not in ['_id', '_rev', 'type'] and key_name not in dynamically_calculated_attributes:
        return True
    return False

# TODO we need a more systematic way of dealing with expected and unexpected get/post parameters
def get_paging_info_from_request(request):
    # TODO this just serves admin.  And it's clunky with the strings.  We need to merge it with the other paging info stuff
    # but the below breaks it for now
    # page = get_parameter('page', default=0, cast_function=int)
    # items_per_page = get_parameter('items_per_page', default=0, cast_function=int)
    # TODO use get_parameter to cast to ints and default to zero
    (page_number, items_per_page) = (0, 0)
    if 'page_number' in request.args.keys() and 'items_per_page' in request.args.keys():
        page_number = request.args['page']
        items_per_page = request.args['items_per_page']
    return (page_number, items_per_page)

def cast_uuid_to_string(item_id):
    if type(item_id).__name__ == 'UUID':
        item_id = str(item_id)
    return item_id

def get_document(doc_id):
    '''
    Fetches a document with the supplied id from the database
    '''
    doc_id = cast_uuid_to_string(doc_id)
    if item_exists(doc_id):
        return current_app.db[doc_id]
    return None

def get_singleton_document(doc_type):
    '''
    Fetches a document that we expect only of its type to exist
    Throws NotFoundError if there are zero or more than one of them in the db
    Throws DocumentConfigurationError if more than one of them are found
    '''
    top_level_document_dict = get_documents_from_criteria({'type': doc_type})
    if len(top_level_document_dict.keys()) > 1:
        raise DocumentConfigurationError('more than one document found of type {0}, expected singleton'.format(doc_type))
    elif len(top_level_document_dict.keys()) == 0:
        raise NotFoundError('no document found of type {0}, expected singleton'.format(doc_type))
    else:
        return top_level_document_dict[top_level_document_dict.keys()[0]]

def save_document(document_in):
    '''
    Saves any document
    Gets doc id from the _id field
    Has safeguards to avoid changing document type
    Has safeguards to avoid saving derived properties
    '''
    if '_id' not in document_in:
         raise DocumentConfigurationError('trying to save the document with no id')
    document_in['_id'] = cast_uuid_to_string(document_in['_id'])  # cast id to string if it's a uuid, couchdb needs that
    the_id = document_in['_id']
    if 'type' not in document_in:
         raise DocumentConfigurationError('trying to save the document with no value for type: {0}'.format(str(the_id)))
    if the_id in current_app.db:
        existing_document = current_app.db[the_id]
        if existing_document['type'] != document_in['type']:
            raise DocumentConfigurationError('attempting to change the document type for document {0}'.format(str(the_id)))
    for dca in dynamically_calculated_attributes:  # remove these properties, they are generated on the fly every retrieve
        if dca in document_in:
            del document_in[dca]
    current_app.db[the_id] = document_in

# TODO throw an error for request args that are present but not specified in args_to_check
def gather_and_enforce_request_args(args_to_check):
    # name, cast_function, required, default are allowed fields.
    # name is the only one that is required
    return_dict = {}

    for arg in args_to_check:
        if arg['name']:
            parameter_name = arg['name']
        else:
            raise DocumentConfigurationError('bad call to gather_and_enforce_request_args: no name supplied')

        if 'cast_function' in arg:
            cast_function = arg['cast_function']
#            try:
#                cast_function = getattr(__builtin__, arg['cast_function'])
#            except Exception as e:
#                error_msg = 'bad call to gather_and_enforce_request_args: no cast function found '\
#                            'for {0}'.format(arg['cast_function'])
#                raise DocumentConfigurationError(error_msg)
        else:
            cast_function = None

        if 'required' in arg:
            required = arg['required']
        else:
            required = False

        if 'default' in arg:
            default = arg['default']
        else:
            default = None

        if parameter_name in request.args:
            return_dict['parameter_name'] = _get_parameter(parameter_name,
                                                           default=default,
                                                           cast_function=cast_function,
                                                           raise_value_error=True)
        else:
            if required:
                raise DocumentConfigurationError('required parameter {0} not supplied in request'.format(parameter_name))
    return return_dict


def _get_parameter(parameter_name, default=None, cast_function=None, raise_value_error=False):
    '''
    Fetches a value from the request args
    You can specify a default value.  If you do not it uses None
    You can specify a default data type.  If you do not it uses string
    If no parameter for that name is found it returns the default
    If you specify a cast_function it will attempt to cast the string using the supplied function
      - If the cast fails and you don't specify raise_value_error it returns the default value
      - If the cast fails and you do specify raise_value_error it raises a ValueError with info in its detail message
    '''
    return_value = default
    if parameter_name in request.args:
        return_value = request.args.get(parameter_name)
        if cast_function:
            try:
                return_value = cast_function(return_value)
            except ValueError as e:
                if raise_value_error:
                    error_string = "problem casting parameter {0} (value {1}) as type {2}".format(str(parameter_name),
                                                                                                  str(return_value),
                                                                                                  str(cast_function.__name__))
                    raise ValueError(error_string)
                else:
                    return_value = default
    return return_value
