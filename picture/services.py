from flask import current_app

from thermal.exceptions import NotFoundError

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
    if picture_id in current_app.db:
        picture_dict = current_app.db[picture_id]
    else:
        raise NotFoundError("picture not found for id {0}".format(picture_id))
    return picture_dict
