import os
import shutil
import uuid

import boto
from flask import current_app
from flask.ext.mail import Message

from picture.services import find_pictures, build_picture_path, build_picture_name, update_picture_document
from thermal.appmodule import mail
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
                  'merge_type': 'colorize_screen',
                  'retake_picam_pics_when_dark': True,
                  'use_gallery': True,
                  'email_recipients': '',
                  'send_email_contents': 'merge',
                  'colorize_range_low': '#000080',
                  'colorize_range_high': '#FFD700',
                  'picam_brightness_threshold': '5.0',
                  'capture_type': 'both_still',
                  'image_sources_to_delete': 'analysis',
                  'use_gallery': False,
                  'image_sources_for_gallery': 'merge',
                  'button_active': True,
                  'type': 'group'}
    return group_dict


def default_settings_dict(group_id):
    settings_id = uuid.uuid4()
    settings_dict = {'_id': str(settings_id),
                     'current_group_id': str(group_id),
                     'type': 'settings'}
    return settings_dict


# TODO reschedule if we don't have internet (actually that's better for the task to do)
def upload_files_to_s3(snap_id, group_id):
    group_document = get_group_document(group_id)
    if group_document['use_gallery']:
        image_sources_for_gallery = group_document['image_sources_for_gallery'].split(',')
        pictures = find_pictures({'snap_id': str(snap_id)})
        # TODO the following assumes s3 and internet are working fine, make it more robust, with py.test tests too
        conn = boto.connect_s3(current_app.config['S3_ACCESS_KEY_ID'], current_app.config['S3_SECRET_ACCESS_KEY'])
        bucket = conn.get_bucket(current_app.config['S3_BUCKET_NAME'])
        for pic_id in pictures.keys():
            if pictures[pic_id]['source'] in image_sources_for_gallery:
                destination = boto.s3.key.Key(bucket)
                destination.key = pictures[pic_id]['filename']
                destination.set_contents_from_filename(pictures[pic_id]['uri'])
                destination.make_public()
                pic_gallery_url = destination.generate_url(expires_in=0, query_auth=False)
                pictures[pic_id]['gallery_url'] = pic_gallery_url
                update_picture_document(pictures[pic_id])


# TODO add tests related to image_sources_to_delete
def clean_up_files(snap_id, group_id):
    group_document = get_group_document(group_id)
    if 'image_sources_to_delete' in group_document:
        image_sources_to_delete = group_document['image_sources_to_delete'].split(',')
    pictures = find_pictures({'snap_id': str(snap_id)})
    for pic_id in pictures.keys():
        if pictures[pic_id]['source'] in image_sources_to_delete:
            os.remove(pictures[pic_id]['uri'])
            pictures[pic_id]['uri'] = ''
            pictures[pic_id]['deleted'] = True
        else:
            shutil.move(pictures[pic_id]['uri'], current_app.config['PICTURE_SAVE_DIRECTORY'])
            pictures[pic_id]['uri'] = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], pictures[pic_id]['filename'])
        update_picture_document(pictures[pic_id])
    os.rmdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))


# TODO add unit tests
def send_mail(snap_id, group_id):
    group_document = get_group_document(group_id)
    if ('email_recipients' in group_document and
            'send_email_contents' in group_document and
            group_document['email_recipients'] and
            group_document['send_email_contents']):
        pics_have_been_attached = False

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
