import os
import shutil
import uuid

import boto
from flask import current_app, url_for
from flask.ext.mail import Message

from picture.services import (find_pictures,
                              build_picture_path,
                              build_picture_name,
                              update_picture_document)
from thermal.appmodule import mail
from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import (get_documents_from_criteria,
                           get_url_base, 
                           save_document)


def get_settings_document():
    '''
    Fetches the settings document (a singleton)
    '''
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


def get_group_document(group_id):
    '''
    Fetches the group document specified by the requested id
    '''
    if group_id == 'current':
        settings_dict = get_settings_document()
        group_id = settings_dict['current_group_id']
    if group_id in current_app.db:  # TODO this is fragile, make into one if using item_exists and get_documents_by_criteria
        group_dict = current_app.db[group_id]
        if group_dict['type'] == 'group':
            return group_dict
    raise NotFoundError('no group document found for id {0}'.format(str(group_id)))


def get_group_document_with_child_objects(group_id):
    '''
    Fetches the group document specified by the requested id
    Also provides links to child photo objects in a child array called snap_list
    '''
    group_dict = get_group_document(group_id)
    group_dict['snap_list'] = get_picture_objects_for_group(group_id)
    return group_dict


def get_picture_objects_for_group(group_id):  # TODO add testing
    '''
    Gets all the pictures belonging to a group, groups them in an array under the snaps they belong to
    '''
    url_base = get_url_base()
    picture_links = []
    args_dict = {}
    snaps_dict = {}
    snaps = []
    args_dict['type'] = 'picture'
    args_dict['group_id'] = group_id
    pictures_dict = get_documents_from_criteria(args_dict)
    for picture_id in pictures_dict:
        picture_link = url_base + url_for('picture.get_picture', picture_id=picture_id)
        snap_id =  pictures_dict[picture_id]['snap_id']
        if snap_id in snaps_dict:
            snaps_dict[snap_id]['picture_objects'].append(pictures_dict[picture_id])
        else:
            snaps_dict[snap_id] = {'created': pictures_dict[picture_id]['created'],
                                   'id': snap_id,
                                   'picture_objects': [pictures_dict[picture_id]]}
    snaps_array = snaps_dict.values()
    snaps_array.sort(key=lambda x: x['created'])
    return snaps_array


def get_group_document_with_child_links(group_id):
    '''
    Fetches a group document, adds a picture_links array to it which has links to all the photos for that group
    '''
    group_dict = get_group_document(group_id)
    group_dict['picture_links'] = get_picture_links_for_group(group_id)
    return group_dict


def get_picture_links_for_group(group_id):  # TODO add testing
    '''
    Gets all the pictures belonging to a given group id
    '''
    # TODO sort these ascending on time
    url_base = get_url_base()
    picture_links = []
    args_dict = {}
    args_dict['type'] = 'picture'
    args_dict['group_id'] = group_id
    pictures_dict = get_documents_from_criteria(args_dict)
    for picture_id in pictures_dict:
        picture_link = url_base + url_for('picture.get_picture', picture_id=picture_id)
        picture_links.append(picture_link)
    return picture_links


def default_group_dict():
    '''
    Wrapper method returning a dict with the default group settings.
    '''
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
    '''
    Wrapper method returning a dict with the default values settings.
    Takes the group id, the only useful data to speak of in this object.
    '''
    settings_id = uuid.uuid4()
    settings_dict = {'_id': str(settings_id),
                     'current_group_id': str(group_id),
                     'type': 'settings'}
    return settings_dict


def create_default_settings_and_group_documents():
    '''
    Creates a settings object and group object with their default settings.  Saves both objects.
    '''
    group_dict = default_group_dict()
    settings_dict = default_settings_dict(group_dict['_id'])
    save_document(settings_dict)
    save_document(group_dict)
    return settings_dict


# TODO reschedule if we don't have internet (actually that's better for the task to do)
def upload_files_to_s3(snap_id, group_id):
    '''
    Uploads pictures for a given snap to s3
    Takes a snap id and group id, if the group is configured to use a gallery it looks for all pictures whose
      values for source matches those are specified in the group to use for the gallery
    '''
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
    '''
    Deletes all picture files for a given snap if those pictures sources are designated in the group to be deleted after processing
    '''
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
    '''
    Sends an email to users specified in the group, with all the images for a supplied snap
    '''
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


# TODO add tests
def find_groups(args_dict, **kwargs):
    '''
    Retrieves a dict of all groups.  Key is the group id, value is the dict for the group.
    '''
    args_dict['type'] = 'group'
    groups_dict = get_documents_from_criteria(args_dict, **kwargs)
    return groups_dict
