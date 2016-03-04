from collections import OrderedDict

from flask import current_app, request

from thermal.exceptions import DocumentConfigurationError


dynamically_calculated_attributes = ['current_group_link', 'picture_links', 'snap_list']


def get_documents_from_criteria(args_dict, **kwargs):
    '''
    Takes key value pairs in an args dict and does a query against the database, testing for equality on all pairs.
    Also supports a few special kwargs to handle things like testing for a key not being null, or paging
    '''
    # TODO have this add virtual properties
    documents_dict = {}
    criteria_list = []
    if 'gallery_url_not_null' in kwargs:
        criteria_list.append("doc.gallery_url != null")
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
    if 'page' in kwargs and kwargs['page'] and 'items_per_page' in kwargs and kwargs['items_per_page']:
        try:
            items_per_page = int(kwargs['items_per_page'])
        except ValueError as e:
            raise DocumentConfigurationError('invalid number specified for items_per_page: {0}'.format(kwargs['items_per_page']))
        try:
            page = int(kwargs['page'])
        except ValueError as e:
            raise DocumentConfigurationError('invalid number specified for page: {0}'.format(kwargs['page']))
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page - 1
        if page < 1:
            raise DocumentConfigurationError('page number must be a number greater than zero')
        if items_per_page < 1:
            raise DocumentConfigurationError('items_per_page must be a number greater than zero')
        paging_requested = True
    return (paging_requested, start_index, end_index)

def get_url_base():
    return request.environ['wsgi.url_scheme'] + '://' + request.environ['HTTP_HOST']

def item_exists(item_id, item_type):
    item_id = str(item_id)  # cast to a string in case it's a uuid
    if item_id and item_id in current_app.db:
        item_dict = current_app.db[item_id]
        if item_dict['type'] == item_type:
            return True
    return False

def doc_attribute_can_be_set(key_name):
    if key_name not in ['_id', '_rev', 'type'] and key_name not in dynamically_calculated_attributes:
        return True
    return False

# TODO we need a more systematic way of dealing with expected and unexpected get/post parameters
def get_paging_info_from_request(request):
    (page, items_per_page) = (0, 0)
    if 'page' in request.args.keys() and 'items_per_page' in request.args.keys():
        page = request.args['page']
        items_per_page = request.args['items_per_page']
    return (page, items_per_page)

def save_document(document_in):
    '''
    Saves any document
    Gets doc id from the _id field
    Has safeguards to avoid changing document type
    Has safeguards to avoid saving derived properties
    '''
    the_id = document_in['_id']
    if the_id in current_app.db:
        existing_document = current_app.db[the_id]
        if existing_document['type'] != document_in['type']:
            raise DocumentConfigurationError('attempting to change the document type for document {0}'.format(str(the_id)))
    for dca in dynamically_calculated_attributes:  # remove these properties, they are generated on the fly every retrieve
        if dca in document_in:
            del document_in[dca]
    current_app.db[the_id] = document_in
