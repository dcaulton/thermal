import os
from mock import ANY, call, Mock, patch
import uuid

import boto
from flask import current_app
import pytest

import admin.services as adms
import conftest
from picture.services import (build_picture_name,
                              build_picture_path)
from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.services import save_generic
from thermal.utils import get_document, item_exists, save_document


class TestServicesUnit(object):
    # TODO add test case for upload_to_s3 if we don't have use_gallery in the group doc

    @patch('admin.services.update_generic')
    @patch('boto.connect_s3')
    @patch('boto.s3.key.Key')
    @patch('admin.services.search_generic')
    @patch('admin.services.get_group_document')
    def test_upload_files_to_s3_calls_expected_methods(self,
                                                       as_get_group_document,
                                                       as_search_generic,
                                                       boto_s3_key_key,
                                                       boto_connect_s3,
                                                       as_update_generic):
        class MockObject(object):
            pass
        the_pictures = {
            "key_1": {
                "uri": "uri_1",
                "filename": "filename_1",
                "source": "analysis"
            },
            "key_2": {
                "uri": "uri_2",
                "filename": "filename_2",
                "source": "merge"
            }
        }
        expected_updated_picture_document = {
            "uri": "uri_2",
            "filename": "filename_2",
            "gallery_url": "the_generated_url",
            "source": "merge"
        }
        as_get_group_document.return_value = {'use_gallery': True,
                                              'image_sources_for_gallery': 'merge'}
        as_search_generic.return_value = the_pictures
        the_mock_bucket = MockObject()
        the_mock_connection = MockObject()
        the_mock_connection.get_bucket = Mock(return_value=the_mock_bucket)
        the_mock_destination = MockObject()
        the_mock_destination.set_contents_from_filename = Mock()
        the_mock_destination.make_public = Mock()
        the_mock_destination.generate_url = Mock(return_value='the_generated_url')
        boto = Mock()
        boto_connect_s3.return_value = the_mock_connection
        boto_s3_key_key.return_value = the_mock_destination

        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        adms.upload_files_to_s3(snap_id, group_id)

        as_get_group_document.assert_called_once_with(group_id)
        as_search_generic.assert_called_once_with(document_type='picture',
                                                  args_dict={'snap_id': str(snap_id)})
        connect_s3_call = call(current_app.config['S3_ACCESS_KEY_ID'], current_app.config['S3_SECRET_ACCESS_KEY'])
        boto_s3_key_key.assert_called_once_with(the_mock_bucket)
        boto_connect_s3.assert_has_calls([connect_s3_call])
        the_mock_connection.get_bucket.assert_called_once_with(current_app.config['S3_BUCKET_NAME'])
        the_mock_destination.set_contents_from_filename.assert_called_once_with("uri_2")
        the_mock_destination.make_public.assert_called_once_with()
        as_update_generic.assert_called_once_with(expected_updated_picture_document, 'picture')


    @patch('admin.services.get_group_document')
    @patch('os.environ.get')
    @patch('admin.services.search_generic')
    @patch('admin.services.build_picture_name')
    @patch('admin.services.build_picture_path')
    @patch('admin.services.get_file_contents')
    @patch('thermal.appmodule.mail.send')
    def test_send_mail_calls_expected_functions(self,
                                                mail_send,
                                                as_get_file_contents,
                                                as_build_picture_path,
                                                as_build_picture_name,
                                                as_search_generic,
                                                os_environ_get,
                                                as_get_group_document):
        class MockObject(object):
            pass
        as_get_group_document.return_value = {'email_recipients': 'me,myself,I',
                                              'send_email_contents': 'pretty,ugly'}
        os_environ_get.return_value = 'rabbit'

        Message = MockObject()
        mock_message = MockObject()
        Message.return_value = mock_message
        mock_message.body = Mock()

        as_search_generic.return_value = {'1': {'source': 'pretty'},
                                          '2': {'source': 'fish_sticks'},
                                          '3': {'source': 'ugly'}}

        as_build_picture_path.return_value = 'mamas_boy_otis'
        as_build_picture_name.return_value = 'punky_qb'
        as_get_file_contents.return_value = 'groovy'

        mock_message.attach = Mock()
    
        adms.send_mail('some_snap_id', 'some_group_id')

        as_get_group_document.assert_called_once_with('some_group_id')
#        Message.assert_called_once_with('pictures from snap some_snap_id',
#                                        sender='rabbit',
#                                        recipients=['me','myself','I'])
#        mock_message.body.assert_called_once_with("this is the image for snap id some_snap_id \n\n")
        as_search_generic.assert_called_once_with(document_type='picture',
                                                  args_dict={'snap_id': 'some_snap_id'})
        bpn_calls = [call('1'), call('3')]
        as_build_picture_name.assert_has_calls(bpn_calls)
        bpp_calls = [call(picture_name='punky_qb', snap_id='some_snap_id'),
                     call(picture_name='punky_qb', snap_id='some_snap_id')]
        as_build_picture_path.assert_has_calls(bpp_calls)
        as_get_file_contents.assert_has_calls([call('mamas_boy_otis'), call('mamas_boy_otis')])
        mail_send.assert_called_once_with(ANY)


    @patch('admin.services.url_for')
    @patch('admin.services.get_documents_from_criteria')
    @patch('admin.services.get_url_base')
    def test_get_picture_links_for_group_calls_expected_methods(self,
                                                                as_get_url_base,
                                                                as_get_documents_from_criteria,
                                                                as_url_for):
        as_get_url_base.return_value = 'mandrill-'
        as_get_documents_from_criteria.return_value = {'cholo': {}, 'payaso': {}}
        as_url_for.return_value = 'baboon'

        return_value = adms.get_picture_links_for_group('some_group_id')

        as_get_url_base.assert_called_once_with()
        as_get_documents_from_criteria.assert_called_once_with({'type': 'picture', 'group_id': 'some_group_id'})
        as_url_for.assert_has_calls([call('picture.get_picture', picture_id='cholo'),
                                     call('picture.get_picture', picture_id='payaso')])
        assert return_value == ['mandrill-baboon', 'mandrill-baboon']


class TestServicesIntegration(object):

    def test_default_settings_dict_has_expected_fields(self):
        the_group_id = uuid.uuid4()
        settings_doc = adms.default_settings_dict(the_group_id)
        expected_fields = ['_id', 'current_group_id', 'type']
        for field in expected_fields:
            assert field in settings_doc
        assert len(settings_doc.keys()) == len(expected_fields)

    def test_default_group_dict_has_expected_fields(self):
        group_doc = adms.default_group_dict()
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

    def test_get_settings_fetches_a_real_settings_document(self):
        settings_doc = adms.get_settings_document()
        assert '_id' in settings_doc.keys()
        assert '_rev' in settings_doc.keys()
        assert 'current_group_id' in settings_doc.keys()
        assert settings_doc['type'] == 'settings'

    def test_settings_points_to_a_real_group_document(self):
        settings_doc = adms.get_settings_document()
        group_doc = current_app.db[settings_doc['current_group_id']]
        assert group_doc['type'] == 'group'

    def test_get_settings_creates_new_settings_document_if_document_is_missing(self):
        old_settings_doc = adms.get_settings_document()
        old_settings_id = old_settings_doc['_id']
        current_app.db.delete(old_settings_doc)
        new_settings_doc = adms.get_settings_document()
        new_settings_id = new_settings_doc['_id']
        assert old_settings_id != new_settings_id

    def test_get_group_document_fails_if_doc_is_not_of_type_group(self):
        the_id = str(uuid.uuid4())
        the_doc = {'type': 'not_group'}
        current_app.db[the_id] = the_doc
        with pytest.raises(NotFoundError):
            the_returned_doc = adms.get_group_document(the_id)

    def test_get_group_document_succeeds_if_doc_is_of_type_group(self):
        the_id = str(uuid.uuid4())
        the_doc = {'type': 'group'}
        current_app.db[the_id] = the_doc
        the_returned_doc = adms.get_group_document(the_id)
        assert the_returned_doc['_id'] == the_id

    def test_get_group_document_current_gets_the_current_group_document(self):
        settings_doc = adms.get_settings_document()

        some_other_group_id = str(uuid.uuid4())
        some_other_group_doc = {'type': 'group'}
        current_app.db[some_other_group_id] = some_other_group_doc

        group_doc_from_current = adms.get_group_document('current')

        assert group_doc_from_current['_id'] != some_other_group_id
        assert group_doc_from_current['_id'] == settings_doc['current_group_id']

    def build_three_pictures(self, snap_id):
        pic_ids = []
        for i in range(1, 3):
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
            save_generic(the_doc, 'picture')
            pic_ids.append(pic_id)
            # touch the picture file in the temp directory
            with open(picture_path, 'a'):
                os.utime(picture_path, None)
            if not item_exists(snap_id, 'snap'):
                snap_doc = {'_id': snap_id,
                            'type': 'snap',
                            'clean_up_files': True}
                save_generic(snap_doc, 'snap')
        return pic_ids

    def test_clean_up_files_cleans_pictures_from_the_snap_and_updates_snap_document(self):
        snap_id = uuid.uuid4()
        group_id = adms.get_group_document('current')['_id']
        pic_ids = self.build_three_pictures(snap_id)
        for pic_id in pic_ids:
            pic_doc = get_document(pic_id)
            assert os.path.isfile(pic_doc['uri'])
            assert str(snap_id) in pic_doc['uri']

        assert os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))
        with current_app.test_request_context('/whatever'):  # needs a context because clean_up_files calls search_generic
            adms.clean_up_files(snap_id, group_id)

        for pic_id in pic_ids:
            pic_doc = get_document(pic_id)
            filename = build_picture_name(pic_id)
            expected_picture_path = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], filename)
            assert pic_doc['uri'] == expected_picture_path
            assert os.path.isfile(expected_picture_path)
        assert not os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))
        snap_document = get_document(snap_id)
        assert snap_document['files_have_been_cleaned_up'] == True

