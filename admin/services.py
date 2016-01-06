import uuid

from flask import current_app

from thermal.exceptions import NotFoundError

def get_settings_document():
    map_fun = '''function(doc) {
        if (doc.type == 'settings')
            emit(doc._id, doc);
    }'''
    view_result = current_app.db.query(map_fun)
    if view_result.total_rows:
        settings_dict = view_result.rows[0]['value']
    else:
        settings_dict = create_default_settings_and_group_documents()
    return settings_dict

def save_document(dict_in):
    current_app.db[dict_in['_id']] = dict_in

def get_group_document(group_id):
    if group_id == 'current':
        settings_dict = get_settings_document()
        group_id = settings_dict['current_group_id']
    if group_id in current_app.db:
        group_dict = current_app.db[group_id]
    else:
        raise NotFoundError('no group document found for id {0}'.format(str(group_id)))
    return group_dict

def create_default_settings_and_group_documents():
    group_dict = default_group_dict()
    settings_dict = default_settings_dict(group_dict['_id'])
    save_document(settings_dict)
    save_document(group_dict)
    return settings_dict

def default_group_dict():
    group_id = uuid.uuid4()
    group_dict = {'_id': str(group_id),
                  'merge_type': 'screen',
                  'retake_picam_pics_when_dark': True,
                  'colorize_range_low': '#000080',
                  'colorize_range_high': '#FFD700',
                  'type': 'group'
    }
    return group_dict

def default_settings_dict(group_id):
    settings_id = uuid.uuid4()
    settings_dict = {'_id': str(settings_id),
                     'current_group_id': str(group_id),
                     'capture_type': 'both_still',
                     'button_active': True,
                     'type': 'settings'
    }
    return settings_dict
