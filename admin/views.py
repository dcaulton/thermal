from flask import Blueprint, request, Response, url_for
import json

from admin.services import (default_group_dict,
                            get_settings_document,
                            get_group_document,
                            get_group_document_with_child_links,
                            get_group_document_with_child_objects)
from thermal.services import save_generic, search_generic
from thermal.utils import (doc_attribute_can_be_set,
                           gather_and_enforce_request_args,
                           get_url_base,
                           dynamically_calculated_attributes)
from thermal.views import (generic_get_view,
                           generic_list_view,
                           generic_save_view)


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
            # TODO change this to update_generic
            save_generic(settings, 'settings')
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
    # If no settings or groups yet create a group
    group_dict = get_group_document('current')
    return generic_list_view(document_type='group')


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
    # TODO in theory get_group_document could throw an exception that turns into a 500
    group_dict = get_group_document(group_id)
    group_id = group_dict['_id']
    return generic_list_view(document_type='picture',
                             args_dict={'group_id': group_id})

@admin.route('/groups/<group_id>/gallery', methods=['GET'])
def get_group_gallery(group_id):
    '''
    Fetches the photo gallery for a supplied group id
    Includes paging and searching on any field in the picture document
    '''
    # TODO in theory get_group_document could throw an exception that turns into a 500
    group_dict = get_group_document(group_id)
    group_id = group_dict['_id']
    return generic_list_view(document_type='picture',
                             args_dict={'group_id': group_id, 'gallery_url_not_null': True})

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
            # TODO change this to update_generic
            save_generic(group_dict, 'group')
            return Response(json.dumps(group_dict), status=200, mimetype='application/json')
        return Response(json.dumps('problem with request data'), status=409, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')


@admin.route('/groups', methods=['POST'])
def save_group():
    '''
    Creates a new group record, saves it as the new current group in the settings document
    Won't let you specify _id, _rev or type
    Automatically sets settings.current_group_id to the groups id as well
    '''
    return_value = generic_save_view(args_dict=default_group_dict(), document_type='group')
    if return_value.status_code == 200:
        try:
            group_id = json.loads(return_value.data)['_id']
            settings = get_settings_document()
            settings['current_group_id'] = group_id
            save_generic(settings, 'settings')
            return return_value
        except Exception as e:
            return Response(json.dumps('error saving settings: '+e.message), status=e.status_code, mimetype='application/json')
    else:
        return return_value

@admin.route('/snaps')
def list_snaps():
    '''
    Lists all snaps
    Supports paging and filtering on any attribute via get parms
    '''
    return generic_list_view(document_type='snap')


@admin.route('/snaps/<snap_id>', methods=['GET'])
def get_snap(snap_id):
    '''
    Fetches an individual calibration session
    '''
    return generic_get_view(item_id=snap_id, document_type='snap')


# snaps are only created implicitly, need for a create here
@admin.route('/snaps/<snap_id>', methods=['PUT'])
def update_snap(snap_id):
    try:
        # TODO add update_generic logic here when it's ready
        return Response(json.dumps('x'), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
