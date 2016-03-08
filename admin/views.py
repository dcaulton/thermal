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
from thermal.utils import (doc_attribute_can_be_set,
                           gather_and_enforce_request_args,
                           get_url_base,
                           dynamically_calculated_attributes)

admin = Blueprint('admin', __name__)


@admin.route('/')
def index():
    '''
    Returns top level links to the 'get settings' and 'list groups' views 
    '''
    url_base = get_url_base()
    top_level_links = {
        'settings': url_base + url_for('admin.get_settings'),
        'groups': url_base + url_for('admin.list_groups'),
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')


# TODO add a test on the service side to check the integrity of settings.current_group_id on settings save.
#   we don't need to worry about deletes, just updates
@admin.route('/settings', methods=['GET'])
def get_settings():
    '''
    Returns the settings document (it's a singleton)
    '''
    try:
        settings = get_settings_document()
        return Response(json.dumps(settings), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@admin.route('/settings', methods=['PUT'])
def update_settings():
    '''
    Updates the settings document
    '''
    try:
        settings = get_settings_document()
        if request.headers['Content-Type'] == 'application/json':
            for k in request.json.keys():
                if doc_attribute_can_be_set(k):
                    settings[k] = request.json[k]
            save_document(settings)
            return Response(json.dumps(settings), status=200, mimetype='application/json')
        err_msg = 'no valid settings parameters supplied'
        return Response(json.dumps(err_msg), status=409, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@admin.route('/groups')
def list_groups():
    '''
    Lists all groups
    Includes paging and searching on any field in the group document
    '''
    try:
        search_dict = gather_and_enforce_request_args(['ANY_SEARCHABLE'])
        groups = find_groups(search_dict)
        return Response(json.dumps(groups), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@admin.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    '''
    Gets a particular group
    supports these levels of information:
     - group dict only
     - links to photos 
     - photos included, grouped by snap id
    '''
    try:
        if 'child_objects' in request.args:  # TODO add documentation in sphinx
            group_dict = get_group_document_with_child_objects(group_id)
        elif 'child_links' in request.args:  # TODO add documentation in sphinx
            group_dict = get_group_document_with_child_links(group_id)
        else:
            group_dict = get_group_document(group_id)
        return Response(json.dumps(group_dict), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@admin.route('/groups/<group_id>/pictures', methods=['GET'])
def get_group_pictures(group_id):
    '''
    Fetches pictures for a supplied group id
    Includes paging and searching on any field in the picture document
    '''
    try:
        group_dict = get_group_document(group_id)
        group_id = group_dict['_id']
        args_dict = gather_and_enforce_request_args(['ANY_SEARCHABLE'])
        args_dict['group_id'] = group_id
        pictures_dict = find_pictures(args_dict)
        return Response(json.dumps(pictures_dict), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@admin.route('/groups/<group_id>/gallery', methods=['GET'])
def get_group_gallery(group_id):
    '''
    Fetches the photo gallery for a supplied group id
    Includes paging and searching on any field in the picture document
    '''
    try:
        group_dict = get_group_document(group_id)
        group_id = group_dict['_id']
        args_dict = gather_and_enforce_request_args(['ANY_SEARCHABLE'])
        args_dict['group_id'] = group_id
        args_dict['gallery_url_not_null'] = True
        pictures_dict = find_pictures(args_dict)
        return Response(json.dumps(pictures_dict), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@admin.route('/groups/<group_id>', methods=['PUT'])
def update_group(group_id):
    '''
    Updates group record
    '''
    try:
        group_dict = get_group_document(group_id)
        if request.headers['Content-Type'] == 'application/json':
            for k in request.json.keys():
                if doc_attribute_can_be_set(k):
                    group_dict[k] = request.json[k]
            save_document(group_dict)
            return Response(json.dumps(group_dict), status=200, mimetype='application/json')
        return Response(json.dumps('problem with request data'), status=409, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@admin.route('/groups', methods=['POST'])
def save_group():
    '''
    Creates a new group record, saves it as the new current group in the settings document
    '''
    try:
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
        return Response(json.dumps('problem with request data'), status=409, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
