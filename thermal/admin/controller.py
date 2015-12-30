import datetime
from flask import g, Blueprint, Flask, request, Response, current_app
import json
import os
import sys
import uuid

admin = Blueprint('admin', __name__)

def get_settings_document():
    map_fun = '''function(doc) {
        if (doc.type == 'settings')
            emit(doc._id, doc);
    }'''
    view_result = g.db.query(map_fun)
    if view_result.total_rows:
        settings_dict = view_result.rows[0]['value']
    else:
        settings_id = uuid.uuid4()
        current_group_id = uuid.uuid4()
        settings_dict = {'_id': str(settings_id),
                         'current_group_id': str(current_group_id),
                         'type': 'settings'
                        }
        g.db[str(settings_id)] = settings_dict
    return settings_dict
    
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
        g.db[settings['_id']] = settings
        return Response(json.dumps(settings), status=200, mimetype='application/json')
