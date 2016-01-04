from couchdb.http import ResourceNotFound
from flask import current_app

def find_pictures():
    pictures_dict = {}
    map_fun = '''function(doc) {
        if (doc.type == 'picture')
            emit(doc._id, doc);
    }'''
    for row in current_app.db.query(map_fun).rows:
        pictures_dict[row['key']] = row['value']
    return pictures_dict
    
def find_picture(picture_id):
    picture_dict = {}
    try:
        picture_dict = current_app.db[picture_id]
    except ResourceNotFound as e:
        pass
    return picture_dict
