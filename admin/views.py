from flask import Blueprint, request, Response, url_for
import json

from admin.services import (default_group_dict,
                            find_groups,
                            get_settings_document,
                            get_group_document,
                            save_document)
from picture.services import find_pictures
from thermal.exceptions import NotFoundError
from thermal.utils import get_url_base

admin = Blueprint('admin', __name__)


@admin.route('/')
def index():
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
    settings = get_settings_document()
    return Response(json.dumps(settings), status=200, mimetype='application/json')


@admin.route('/settings', methods=['PUT'])
def update_settings():
    settings = get_settings_document()
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if doc_attribute_can_be_set(k):
                settings[k] = request.json[k]
        save_document(settings)
        return Response(json.dumps(settings), status=200, mimetype='application/json')


# TODO add tests
@admin.route('/groups')
def list_groups():
    search_dict = {}
    for key in request.args.keys():
        search_dict[key] = request.args[key]
    groups = find_groups(search_dict)
    return Response(json.dumps(groups), status=200, mimetype='application/json')


@admin.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    try:
        group_dict = get_group_document(group_id)
    except NotFoundError as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
    return Response(json.dumps(group_dict), status=200, mimetype='application/json')


@admin.route('/groups/<group_id>/pictures', methods=['GET'])
def get_group_pictures(group_id):
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
    group_dict = get_group_document(group_id)
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if doc_attribute_can_be_set(k):
                group_dict[k] = request.json[k]
        save_document(group_dict)
        return Response(json.dumps(group_dict), status=200, mimetype='application/json')


@admin.route('/groups', methods=['POST'])
def save_group():
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
    if key_name not in ['_id', '_rev']:
        return True
    return False


# TODO we need a more systematic way of dealing with expected and unexpected get/post parameters
def get_paging_info_from_request(request):
    (page, items_per_page) = (0, 0)
    if 'page' in request.args.keys() and 'items_per_page' in request.args.keys():
        page = request.args['page']
        items_per_page = request.args['items_per_page']
    return (page, items_per_page)
