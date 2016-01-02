import json

import couchdb
from flask import g, Blueprint, Flask, request, Response, current_app

picture = Blueprint('picture', __name__)

def find_pictures():
    pictures_dict = {}
    map_fun = '''function(doc) {
        if (doc.type == 'picture')
            emit(doc._id, doc);
    }'''
    for row in g.db.query(map_fun).rows:
        pictures_dict[row['key']] = row['value']
    return pictures_dict
    
@picture.route('/')
def list_pictures():
    pictures = find_pictures()
    return Response(json.dumps(pictures), status=200, mimetype='application/json')

@picture.route('/<picture_id>')
def get_picture(picture_id):
    try:
        picture_dict = g.db[picture_id]
        return Response(json.dumps(picture_dict), status=200, mimetype='application/json')
    except couchdb.http.ResourceNotFound as e:
        return Response('not found', status=404)
