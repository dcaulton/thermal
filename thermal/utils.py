from flask import current_app, request

from thermal.exceptions import DocumentConfigurationError


def get_documents_from_criteria(args_dict, **kwargs):
    '''
    Takes key value pairs in an args dict and does a query against the database, testing for equality on all pairs.
    Also supports a few special kwargs to handle things like testing for a key not being null, or paging
    '''
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
