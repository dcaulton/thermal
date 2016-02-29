from flask import Blueprint, request, Response, url_for
import json

from admin.services import (default_group_dict,
                            find_groups,
                            get_settings_document,
                            get_group_document,
                            get_group_document_with_child_links,
                            get_group_document_with_child_objects,
                            save_document)
from picture.services import find_pictures
from thermal.exceptions import NotFoundError
from thermal.utils import get_url_base, dynamically_calculated_attributes

admin = Blueprint('admin', __name__)


@admin.route('/')
def index():
    '''
    Returns a top level index of the admin views
    '''
    url_base = get_url_base()
    top_level_links = {
        'settings': url_base + url_for('admin.get_settings'),
        'groups': url_base + url_for('admin.list_groups'),
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')


# TODO add a test on the service side to check the integrity of settings.current_group_id on settings save.
#   we don't need to worry about deletes, just updates
# TODO add tests for these views
@admin.route('/settings', methods=['GET'])
def get_settings():
    '''
    Returns the settings document (it's a singleton)
    '''
    settings = get_settings_document()
    return Response(json.dumps(settings), status=200, mimetype='application/json')


@admin.route('/settings', methods=['PUT'])
def update_settings():
    '''
    Updates the settings document
    '''
    settings = get_settings_document()
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if doc_attribute_can_be_set(k):
                settings[k] = request.json[k]
        save_document(settings)
        return Response(json.dumps(settings), status=200, mimetype='application/json')
    err_msg = 'no valid settings parameters supplied'
    return Response(json.dumps(err_msg), status=409, mimetype='application/json')


# TODO add tests
@admin.route('/groups')
def list_groups():
    '''
    Lists all groups
    '''
    search_dict = {}
    for key in request.args.keys():
        search_dict[key] = request.args[key]
    groups = find_groups(search_dict)
    return Response(json.dumps(groups), status=200, mimetype='application/json')


@admin.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    '''
    Gets a particular group
    supports these levels of information:
     - group dict only
     - links to photos 
     - photos included, grouped by snap id
    '''
    # TODO support four levels of fetch eventually.
    #  - group dict only
    #  - links to children
    #  - nest full child photo objects, bin photos by 'snap' (a virtual object) with snap id and time also included
    try:
        if 'child_objects' in request.args:  # TODO add documentation in sphinx
            group_dict = get_group_document_with_child_objects(group_id)
        elif 'child_links' in request.args:  # TODO add documentation in sphinx
            group_dict = get_group_document_with_child_links(group_id)
        else:
            group_dict = get_group_document(group_id)
    except NotFoundError as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
    return Response(json.dumps(group_dict), status=200, mimetype='application/json')


@admin.route('/groups/<group_id>/pictures', methods=['GET'])
def get_group_pictures(group_id):
    '''
    Fetches pictures for a supplied group id
    '''
    try:
        group_dict = get_group_document(group_id)
        group_id = group_dict['_id']
        args_dict = {'group_id': group_id}
        (page, items_per_page) = get_paging_info_from_request(request)
        pictures_dict = find_pictures(args_dict, page=page, items_per_page=items_per_page)
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
    return Response(json.dumps(pictures_dict), status=200, mimetype='application/json')


# TODO this will need an integration test.
@admin.route('/groups/<group_id>/gallery', methods=['GET'])
def get_group_gallery(group_id):
    '''
    Fetches the photo gallery for a supplied group id
    '''
    try:
        group_dict = get_group_document(group_id)
        group_id = group_dict['_id']
        args_dict = {'group_id': group_id}
        (page, items_per_page) = get_paging_info_from_request(request)
        pictures_dict = find_pictures(args_dict, gallery_url_not_null=True, page=page, items_per_page=items_per_page)
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
    return Response(json.dumps(pictures_dict), status=200, mimetype='application/json')


@admin.route('/groups/<group_id>', methods=['PUT'])
def update_group(group_id):
    '''
    Updates group record
    '''
    group_dict = get_group_document(group_id)
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if doc_attribute_can_be_set(k):
                group_dict[k] = request.json[k]
        save_document(group_dict)
        return Response(json.dumps(group_dict), status=200, mimetype='application/json')


@admin.route('/groups', methods=['POST'])
def save_group():
    '''
    Creates a new group record
    '''
    settings = get_settings_document()
    group_dict = default_group_dict()
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if doc_attribute_can_be_set(k):
                group_dict[k] = request.json[k]
        save_document(group_dict)
        settings['current_group_id'] = group_dict['_id']
        save_document(settings)
        return Response(json.dumps(group_dict), status=200, mimetype='application/json')


def doc_attribute_can_be_set(key_name):
    # TODO it feels like there is some overlap with this functionality and what is in admin.services.save_document
    if key_name not in ['_id', '_rev'] and key_name not in dynamically_calculated_attributes:
        return True
    return False


# TODO we need a more systematic way of dealing with expected and unexpected get/post parameters
def get_paging_info_from_request(request):
    (page, items_per_page) = (0, 0)
    if 'page' in request.args.keys() and 'items_per_page' in request.args.keys():
        page = request.args['page']
        items_per_page = request.args['items_per_page']
    return (page, items_per_page)
