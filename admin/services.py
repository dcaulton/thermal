import os
import shutil
import uuid

from flask import current_app
from flask.ext.mail import Message

from picture.services import find_pictures, build_picture_path, build_picture_name, update_picture_document
from thermal.appmodule import celery, mail
from thermal.exceptions import DocumentConfigurationError, NotFoundError


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

def save_document(document_in):
    the_id = document_in['_id']
    if the_id in current_app.db:
        existing_document = current_app.db[the_id]
        if existing_document['type'] != document_in['type']:
            raise DocumentConfigurationError('attempting to change the document type for document {0}'.format(str(the_id)))
    current_app.db[the_id] = document_in

def get_group_document(group_id):
    if group_id == 'current':
        settings_dict = get_settings_document()
        group_id = settings_dict['current_group_id']
    if group_id in current_app.db:
        group_dict = current_app.db[group_id]
        if group_dict['type'] == 'group':
            return group_dict
    raise NotFoundError('no group document found for id {0}'.format(str(group_id)))

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
                  'email_recipients': '',
                  'send_email_contents': 'merge',
                  'colorize_range_low': '#000080',
                  'colorize_range_high': '#FFD700',
                  'picam_brightness_threshold': '5.0',
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

@celery.task
def clean_up_files_chained(_, snap_id):
    clean_up_files(snap_id)

def clean_up_files(snap_id):
    pictures = find_pictures({'snap_id': str(snap_id)})
    for pic_id in pictures.keys():
        shutil.move(pictures[pic_id]['uri'], current_app.config['PICTURE_SAVE_DIRECTORY'])
        pictures[pic_id]['uri'] = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], pictures[pic_id]['filename'])
        update_picture_document(pictures[pic_id])
    os.rmdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))

@celery.task
def send_mail_chained(_, snap_id, group_id):
    send_mail(snap_id, group_id)

def send_mail(snap_id, group_id):
    group_document = get_group_document(group_id)
    if ('email_recipients' in group_document and 
        'send_email_contents' in group_document and
        group_document['email_recipients'] and
        group_document['send_email_contents']):

        subject = "pictures from snap {0}".format(snap_id)
        recipients = group_document['email_recipients'].split(',')
        sender_addr = os.environ.get('MAIL_USERNAME')
        msg = Message(subject, sender=sender_addr, recipients=recipients)
        msg.body = "this is the image for snap id {0}\n\n".format(snap_id)

        pictures = find_pictures({'snap_id': str(snap_id)})
        picture_types = group_document['send_email_contents'].split(',')
        for pic_id in pictures.keys():
            if pictures[pic_id]['source'] in picture_types:
                pic_name = build_picture_name(pic_id)
                pic_path = build_picture_path(picture_name=pic_name, snap_id=snap_id)
                with current_app.open_resource(pic_path) as fp:
                    msg.attach(pic_name, "image/jpeg", fp.read())
                    pics_have_been_attached = True
        if pics_have_been_attached:
            mail.send(msg)
