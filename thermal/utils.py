import __builtin__
from collections import OrderedDict

from flask import current_app, request

from thermal.exceptions import DocumentConfigurationError, NotFoundError


dynamically_calculated_attributes = ['current_group_link', 'picture_links', 'snap_list']


# TODO have this add virtual properties?
# TODO escape the strings enough to keep bobby tables out of our hair
def get_documents_from_criteria(args_dict):
    '''
    Takes key value pairs in an args dict, builds in a map string assuming equality checks on each key and value.
    Then it does a query against the database.
    Also supports a few special meta values which are not passed directly into the map string.
    - gallery_url_not_null: adds a test for 'doc.gallery_url != null'  (the only non-equality test we care about for now)
    - page_number, items_per_page - used to perform paging
    '''
    documents_dict = {}
    criteria_list = []
    if 'gallery_url_not_null' in args_dict:
        criteria_list.append("doc.gallery_url != null")
        del args_dict['gallery_url_not_null']
    (paging_requested, start_index, end_index) = get_paging_info_from_args_dict(args_dict)

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

def get_paging_info_from_args_dict(args_dict):
    '''
    Fetches any paging information from the args dict and removes those entries from the dict.
    Starts with page_number and items_per_page, returns a boolean indicating if paging is wanted, and start and end indices
    Will accept page_number=0, items_per_page=0, delete them from args dict and indicate no paging requested
    '''
    paging_requested = False
    start_index = 0
    end_index = 0
    if 'page_number' in args_dict and 'items_per_page' in args_dict:
        try:
            items_per_page = int(args_dict['items_per_page'])
            del args_dict['items_per_page']
        except ValueError as e:
            raise DocumentConfigurationError('invalid number specified for items_per_page: {0}'.format(args_dict['items_per_page']))
        try:
            page_number = int(args_dict['page_number'])
            del args_dict['page_number']
        except ValueError as e:
            raise DocumentConfigurationError('invalid number specified for page_number: {0}'.format(args_dict['page_number']))

        if page_number == 0 and items_per_page == 0:  # If parameters are the defaults assume no paging requested
            return (False, 0, 0)

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
    Not record-specific, we don't really have models with this application.
    '''
    if key_name not in ['_id', '_rev', 'type'] and key_name not in dynamically_calculated_attributes:
        return True
    return False

def cast_uuid_to_string(item_id):
    '''
    Forces a uuid to a string.  Doesn't touch other types of values.
    '''
    if type(item_id).__name__ == 'UUID':
        item_id = str(item_id)
    return item_id

def get_document_with_exception(doc_id, document_type='any'):
    '''
    Fetches a document with the supplied id from the database.
    Throws a NotFoundError if a document of that type isn't available.  Accepts 'any' as a wildcard for document type
    '''
    doc_id = cast_uuid_to_string(doc_id)
    if not item_exists(doc_id, document_type):
        raise NotFoundError("No document of type {0} found for id {1}".format(document_type, doc_id))
    return get_document(doc_id)

def get_document(doc_id):
    '''
    Fetches a document with the supplied id from the database.
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
    Saves any document you give it that has a type and valid _id 
    Strips out dynamically calculated attributes before saving
    Any further safeguards (altering type on update, etc) should be placed in thermal.services that do that work, then call this
    '''
    if '_id' not in document_in:
         raise DocumentConfigurationError('trying to save the document with no id')
    document_in['_id'] = cast_uuid_to_string(document_in['_id'])  # cast id to string if it's a uuid, couchdb needs that
    the_id = document_in['_id']
    if 'type' not in document_in:
         raise DocumentConfigurationError('trying to save the document with no value for type: {0}'.format(str(the_id)))
    for dca in dynamically_calculated_attributes:  # remove these properties, they are generated on the fly every retrieve
        if dca in document_in:
            del document_in[dca]
    current_app.db[the_id] = document_in

def gather_and_enforce_request_args(args_to_check):
    '''
    Single point of calling for gather_and_enforce args calls.
    Decides whether to route to the 'get everything and paging data' submethod, or the one which offers full controls over
    required/optional, defaults, how to cast the values, etc.
    '''
    if args_to_check == ['ANY_SEARCHABLE']:
        return gather_and_enforce_request_args_any_searchable()
    else:
        return gather_and_enforce_request_args_enumerated(args_to_check)

def gather_and_enforce_request_args_any_searchable():
    '''
    Gathers up any request.args that are supplied and puts them into a dict
    Also gathers paging info and puts them in the dict
    Does not check for args that don't belong or have any meaning to this system
    '''
    return_dict = gather_and_enforce_request_args_enumerated([{'name': 'page_number',
                                                               'default': 0,
                                                               'cast_function': int,
                                                               'required': False},
                                                              {'name': 'items_per_page',
                                                               'default': 0,
                                                               'cast_function': int,
                                                               'required': False}])
    for key in request.args.keys():  # now that we have gotten paging data, move the rest of the args over as strings
        if key not in return_dict:  # don't bring paging info over
            return_dict[key] = request.args[key]
    return return_dict

# TODO throw an error for request args that are present but not specified in args_to_check
def gather_and_enforce_request_args_enumerated(args_to_check):
    '''
    Looks at parameters in the request.args and accumulates them to a dict.
    Accepts an array of dicts, each dict having parm name, a function to cast or convert it, if it's required, and a default value.
    Relies on _get_parameter to actually pull values from request.args and cast them.
    For any parameter:
      - if required and absent: throw a DocumentConfigurationError
      - if required and present: get it
      - if optional and present: get it
      - if optional and absent and default specified: get the default
      - if optional and absent and no default specified: dont get anything
      - if there is a value and a cast function and the value fails the cast: pass through the ValueError from _get_parameter
    '''
    # name is the only field that is required
    return_dict = {}
#    requested_keys = request.args.keys()  # TODO this logic, is causing problems with tests for now, needs fixing

    # TODO require args_to_check to be iterable, throw DocumentConfigurationError if not
    for arg in args_to_check:
        if 'name' in arg:
            parameter_name = arg['name']
        else:
            raise DocumentConfigurationError('bad call to gather_and_enforce_request_args: no name supplied')

        if 'cast_function' in arg:
            cast_function = arg['cast_function']
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

        if parameter_name not in request.args and required:
            raise DocumentConfigurationError('required parameter {0} not supplied in request'.format(parameter_name))
        elif parameter_name not in request.args and not required and 'default' not in arg:
            pass
        else:
            return_dict[parameter_name] = _get_parameter(parameter_name,
                                                         default=default,
                                                         cast_function=cast_function,
                                                         raise_value_error=True)

#        if parameter_name in requested_keys:
#            requested_keys.remove(parameter_name)
#    if len(requested_keys):  # error if extra parameters have been supplied
#        raise DocumentConfigurationError('unexpected arguments supplied: {0}'.format(str(requested_keys)))
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
