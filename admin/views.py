from flask import Blueprint, request, Response, current_app
import json

from admin.services import get_settings_document

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
        current_app.db[settings['_id']] = settings
        return Response(json.dumps(settings), status=200, mimetype='application/json')
