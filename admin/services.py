from flask import current_app
import uuid

def get_settings_document():
    map_fun = '''function(doc) {
        if (doc.type == 'settings')
            emit(doc._id, doc);
    }'''
    view_result = current_app.db.query(map_fun)
    if view_result.total_rows:
        settings_dict = view_result.rows[0]['value']
    else:
        settings_id = uuid.uuid4()
        current_group_id = uuid.uuid4()
        settings_dict = {'_id': str(settings_id),
                         'current_group_id': str(current_group_id),
                         'capture_type': 'both_still',
                         'button_active': True,
                         'type': 'settings'
                        }
        current_app.db[str(settings_id)] = settings_dict
    return settings_dict
