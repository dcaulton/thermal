import datetime
from flask import g, Blueprint, Flask, request, Response, current_app
import json
import os
import sys
import uuid

admin = Blueprint('admin', __name__)

current_group_id = uuid.uuid4()

def get_settings_document():
    map_fun = '''function(doc) {
        if (doc.type == 'settings')
            emit(doc._id, doc);
    }'''
    view_result = g.db.query(map_fun)
    if view_result.total_rows:
        return view_result.rows[0]['value']
    else:
        return {'_id': str(uuid.uuid4()),
                'type': 'settings'
               }
    
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
