from flask import Blueprint, request, Response
import json

from admin.services import get_settings_document, get_group_document, save_document

admin = Blueprint('admin', __name__)

@admin.route('/')
def index():
    return 'Admin'

@admin.route('/settings', methods=['GET'])
def get_settings():
    settings = get_settings_document()
    return Response(json.dumps(settings), status=200, mimetype='application/json')
    
@admin.route('/settings', methods=['POST'])
def set_settings():
    settings = get_settings_document()
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if k != '_id':
                settings[k] = request.json[k]
        save_document(settings)
        return Response(json.dumps(settings), status=200, mimetype='application/json')

@admin.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    settings = get_group_document(group_id)
    return Response(json.dumps(settings), status=200, mimetype='application/json')

@admin.route('/groups/<group_id>', methods=['POST'])
def set_group(group_id):
    settings = get_group_document(group_id)
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if k != '_id':
                settings[k] = request.json[k]
        save_document(settings)
        return Response(json.dumps(settings), status=200, mimetype='application/json')
