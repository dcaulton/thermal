import os
import uuid

from flask import current_app
import pytest 

import admin.services
import conftest
from picture.services import build_picture_name, build_picture_path, find_picture, save_picture_document
from thermal.exceptions import DocumentConfigurationError, NotFoundError

class TestSettingsUnit(object):
    def test_default_settings_dict_has_expected_fields(self):
        the_group_id = uuid.uuid4()
        settings_doc = admin.services.default_settings_dict(the_group_id)
        expected_fields = ['_id', 'current_group_id', 'type']
        for field in expected_fields:
            assert field in settings_doc
        assert len(settings_doc.keys()) == len(expected_fields)

    def test_default_group_dict_has_expected_fields(self):
        group_doc = admin.services.default_group_dict()
        expected_fields = ['_id',
                           'merge_type',
                           'retake_picam_pics_when_dark',
                           'email_recipients',
                           'send_email_contents',
                           'colorize_range_low',
                           'colorize_range_high',
                           'picam_brightness_threshold',
                           'capture_type',
                           'image_sources_to_delete',
                           'use_gallery',
                           'image_sources_for_gallery',
                           'button_active',
                           'type']
        for field in expected_fields:
            assert field in group_doc
        assert len(group_doc.keys()) == len(expected_fields)

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
                  'button_active': True,
                  'type': 'group'
    }
    return group_dict



class TestSettingsIntegration(object):
    def test_get_settings_fetches_a_real_settings_document(self):
        settings_doc = admin.services.get_settings_document()
        assert '_id' in settings_doc.keys()
        assert '_rev' in settings_doc.keys()
        assert 'current_group_id' in settings_doc.keys()
        assert settings_doc['type'] == 'settings'

    def test_settings_points_to_a_real_group_document(self):
        settings_doc = admin.services.get_settings_document()
        group_doc = current_app.db[settings_doc['current_group_id']]
        assert group_doc['type'] == 'group'

    def test_get_settings_creates_new_settings_document_if_document_is_missing(self):
        old_settings_doc = admin.services.get_settings_document()
        old_settings_id = old_settings_doc['_id']
        current_app.db.delete(old_settings_doc)
        new_settings_doc = admin.services.get_settings_document()
        new_settings_id = new_settings_doc['_id']
        assert old_settings_id != new_settings_id

    def test_get_group_document_fails_if_doc_is_not_of_type_group(self):
        the_id = str(uuid.uuid4())
        the_doc = {'type': 'not_group'}
        current_app.db[the_id] = the_doc
        with pytest.raises(NotFoundError):
            the_returned_doc = admin.services.get_group_document(the_id)

    def test_get_group_document_succeeds_if_doc_is_of_type_group(self):
        the_id = str(uuid.uuid4())
        the_doc = {'type': 'group'}
        current_app.db[the_id] = the_doc
        the_returned_doc = admin.services.get_group_document(the_id)
        assert the_returned_doc['_id'] == the_id

    def test_get_group_document_current_gets_the_current_group_document(self):
        settings_doc = admin.services.get_settings_document()

        some_other_group_id = str(uuid.uuid4())
        some_other_group_doc = {'type': 'group'}
        current_app.db[some_other_group_id] = some_other_group_doc

        group_doc_from_current = admin.services.get_group_document('current')

        assert group_doc_from_current['_id'] != some_other_group_id
        assert group_doc_from_current['_id'] == settings_doc['current_group_id']

    def test_save_document_fails_if_document_type_is_being_altered(self):
        the_id = str(uuid.uuid4())
        the_doc = {'_id': the_id, 'type': 'something'}
        current_app.db[the_id] = the_doc
        the_doc['type'] = 'something else'
        with pytest.raises(DocumentConfigurationError):
            admin.services.save_document(the_doc)

    def build_three_pictures(self, snap_id):
        pic_ids = []
        for i in range(1,3):
            pic_id = uuid.uuid4()
            filename = build_picture_name(pic_id)
            picture_path = build_picture_path(picture_name=filename, snap_id=snap_id)
            the_doc = {
                '_id': str(pic_id), 
                'snap_id': str(snap_id),
                'uri': picture_path,
                'filename': filename, 
                'source': 'whatever',
                'type': 'picture'
            }
            save_picture_document(the_doc)
            pic_ids.append(pic_id)
            #touch the picture file in the temp directory
            with open(picture_path, 'a'):
                 os.utime(picture_path, None)
        return pic_ids

    def test_clean_up_files_cleans_pictures_from_the_snap(self):
        snap_id = uuid.uuid4()
        group_id = admin.services.get_group_document('current')['_id']
        pic_ids = self.build_three_pictures(snap_id)
        for pic_id in pic_ids:
            pic_doc = find_picture(pic_id)
            assert os.path.isfile(pic_doc['uri'])
            assert str(snap_id) in pic_doc['uri']

        assert os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))
        admin.services.clean_up_files(snap_id, group_id)

        for pic_id in pic_ids:
            pic_doc = find_picture(pic_id)
            filename = build_picture_name(pic_id)
            expected_picture_path = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], filename)
            assert pic_doc['uri'] == expected_picture_path
            assert os.path.isfile(expected_picture_path)
        assert not os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))

# put a 'delete_after_processing' tag on intermediate pictures, like what will be coming from edge detection
### unit tests
