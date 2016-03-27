from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
from PIL import Image, ImageChops
import pytest

from admin.services import get_group_document
import merging.services as ms
from thermal.appmodule import celery
from thermal.exceptions import ThermalBaseError


class TestServicesUnit(object):


    @patch('merging.services.merge_images')
    def test_merge_images_chained_calls_merge_images(self,
                                                     ms_merge_images):
        ms.merge_images_chained('a', 'b', 'c', 'd', 'e', 'f')
        ms_merge_images.assert_called_once_with(img1_primary_id_in='b',
                                                img1_alternate_id_in='c',
                                                img2_id_in='d',
                                                img_id_out='e',
                                                group_id='f')

    @patch('merging.services.merge_images')
    def test_merge_images_task_calls_merge_images(self,
                                                  ms_merge_images):
        ms.merge_images_task('a', 'b', 'c', 'd', 'e')
        ms_merge_images.assert_called_once_with(img1_primary_id_in='a',
                                                img1_alternate_id_in='b',
                                                img2_id_in='c',
                                                img_id_out='d',
                                                group_id='e')

    @patch('merging.services.get_group_document')
    def test_get_merge_type_gets_merge_type_from_group_document(self,
                                                                ms_get_group_document):
        ms_get_group_document.return_value = {'merge_type': 'difference'}
        merge_type = ms.get_merge_type('haha')
        ms_get_group_document.assert_called_once_with('haha')
        assert merge_type == 'difference'

    @patch('merging.services.get_group_document')
    def test_get_merge_type_uses_screen_for_default(self,
                                                    ms_get_group_document):
        ms_get_group_document.return_value = {}
        merge_type = ms.get_merge_type('lala')
        assert merge_type == 'screen'


# TODO figure out how to mock out getattr
#    @patch('merging.services.merge_type_is_valid')
#    @patch('__builtins__.getattr')
#    def test_get_merge_method_fetches_valid_method(self,
#                                                   ms_getattr,
#                                                   ms_merge_type_is_valid):
#        ms_merge_type_is_valid.return_value = True
#        ms.get_merge_method('haha')
#        ms_getattr.assert_called_once_with(ImageChops, 'haha')
#
#    @patch('merging.services.merge_type_is_valid')
#    @patch('__builtins__.getattr')
#    def test_get_merge_method_uses_screen_for_default(self,
#                                                      ms_getattr,
#                                                      ms_merge_type_is_valid):
#        ms_merge_type_is_valid.return_value = False
#        ms.get_merge_method('haha')
#        ms_getattr.assert_called_once_with(ImageChops, 'screen')
#

    @patch('merging.services.get_image_paths_and_snap_id')
    @patch('merging.services.get_merge_type')
    @patch('merging.services.get_merge_method')
    @patch('merging.services.do_image_merge')
    @patch('merging.services.item_exists')
    @patch('merging.services.save_generic')
    def test_merge_images_calls_expected_methods(self,
                                                 ms_save_generic,
                                                 ms_item_exists,
                                                 ms_do_image_merge,
                                                 ms_get_merge_method,
                                                 ms_get_merge_type,
                                                 ms_get_image_paths_and_snap_id):
        ms_item_exists.return_value = False
        the_paths_dict = {'snap_id': 'x',
                          'img_out_filename': 'y',
                          'img_out_path': 'z'}
        ms_get_image_paths_and_snap_id.return_value = the_paths_dict
        ms_get_merge_type.return_value = 'waldorf'
        ms_get_merge_method.return_value = int

        ms.merge_images('a', 'b', 'c', 'd', 'e')

        ms_item_exists.assert_called_once_with('b', 'picture')
        ms_get_image_paths_and_snap_id.assert_called_once_with('a', 'c', 'd')
        ms_get_merge_type.assert_called_once_with('e')
        ms_get_merge_method.assert_called_once_with('waldorf')
        ms_do_image_merge.assert_called_once_with(the_paths_dict, int)
        ms_save_generic.assert_called_once_with({'_id': 'd',
                                                 'type': 'picture',
                                                 'source': 'merge',
                                                 'source_image_id_1': 'a',
                                                 'source_image_id_2': 'c',
                                                 'merge_type': 'waldorf',
                                                 'group_id': 'e',
                                                 'snap_id': 'x',
                                                 'filename': 'y',
                                                 'uri': 'z',
                                                 'created': ANY},
                                                 'picture')


    @patch('merging.services.get_image_paths_and_snap_id')
    @patch('merging.services.get_merge_type')
    @patch('merging.services.get_merge_method')
    @patch('merging.services.do_image_merge')
    @patch('merging.services.item_exists')
    @patch('merging.services.save_generic')
    def test_merge_images_uses_alternate_img1_when_exists(self,
                                                          ms_save_generic,
                                                          ms_item_exists,
                                                          ms_do_image_merge,
                                                          ms_get_merge_method,
                                                          ms_get_merge_type,
                                                          ms_get_image_paths_and_snap_id):
        ms_item_exists.return_value = True
        the_paths_dict = {'snap_id': 'x',
                          'img_out_filename': 'y',
                          'img_out_path': 'z'}
        ms_get_image_paths_and_snap_id.return_value = the_paths_dict
        ms_get_merge_type.return_value = 'waldorf'
        ms_get_merge_method.return_value = int

        ms.merge_images('a', 'b', 'c', 'd', 'e')

        ms_get_image_paths_and_snap_id.assert_called_once_with('b', 'c', 'd')
        ms_save_generic.assert_called_once_with({'_id': 'd',
                                                 'type': 'picture',
                                                 'source': 'merge',
                                                 'source_image_id_1': 'b',
                                                 'source_image_id_2': 'c',
                                                 'merge_type': 'waldorf',
                                                 'group_id': 'e',
                                                 'snap_id': 'x',
                                                 'filename': 'y',
                                                 'uri': 'z',
                                                 'created': ANY},
                                                 'picture')

    @patch('merging.services.get_document_with_exception')
    @patch('merging.services.build_picture_name')
    @patch('merging.services.build_picture_path')
    def test_get_image_paths_and_snap_id_calls_expected_methods(self,
                                                                ms_build_picture_path,
                                                                ms_build_picture_name,
                                                                ms_get_document_with_exception):
        ms_get_document_with_exception.return_value = {'filename': 'some_filename',
                                                       'snap_id': 'some_snap_id'}
        ms_build_picture_name.return_value = 'some_name'
        ms_build_picture_path.return_value = 'some_path'

        return_value = ms.get_image_paths_and_snap_id('one', 'two', 'three')

        ms_get_document_with_exception.assert_has_calls([call('one', 'picture'), call('two', 'picture')])
        ms_build_picture_name.assert_called_once_with('three')

        ms_build_picture_path.assert_has_calls([call(picture_name='some_filename', snap_id='some_snap_id'),
                                                call(picture_name='some_filename', snap_id='some_snap_id'),
                                                call(picture_name='some_name', snap_id='some_snap_id')])

        assert return_value == {'img1_path': 'some_path',
                                'img2_path': 'some_path',
                                'img_out_path': 'some_path',
                                'img_out_filename': 'some_name',
                                'snap_id': 'some_snap_id'}

    def test_do_image_merge_calls_expected_methods(self):
        class MockImage(object):
            pass
        the_mock_image = MockImage()
        the_mock_image.convert = Mock(return_value='strange')
        the_mock_image.save = Mock()
        Image.open = Mock(return_value = the_mock_image)
        the_merge_method = Mock(return_value=the_mock_image)

        ms.do_image_merge({'img1_path': 'a', 'img2_path': 'b', 'img_out_path': 'c'}, the_merge_method)

        Image.open.assert_has_calls([call('a'), call('b')])
        the_merge_method.assert_called_once_with('strange', 'strange')
        the_mock_image.save.assert_called_once_with('c')



    @patch('merging.services.log_asynchronous_exception')
    @patch('merging.services.merge_images')
    def test_merge_images_chained_catches_exception(self,
                                                    ms_merge_images,
                                                    ms_log_asynchronous_exception):
        the_exception = ThermalBaseError('wendy_williams')
        ms_merge_images.side_effect = the_exception

        ms.merge_images_chained('a', 'b', 'c', 'd', 'e', 'f')

        ms_merge_images.assert_called_once_with(img1_primary_id_in='b',
                                                img1_alternate_id_in='c',
                                                img2_id_in='d',
                                                img_id_out='e',
                                                group_id='f')
        ms_log_asynchronous_exception.assert_called_once_with(the_exception)

    @patch('merging.services.log_asynchronous_exception')
    @patch('merging.services.merge_images')
    def test_merge_images_task_catches_exception(self,
                                                 ms_merge_images,
                                                 ms_log_asynchronous_exception):
        the_exception = ThermalBaseError('wendy_williams')
        ms_merge_images.side_effect = the_exception

        ms.merge_images_task('a', 'b', 'c', 'd', 'e')

        ms_merge_images.assert_called_once_with(img1_primary_id_in='a',
                                                img1_alternate_id_in='b',
                                                img2_id_in='c',
                                                img_id_out='d',
                                                group_id='e')
        ms_log_asynchronous_exception.assert_called_once_with(the_exception)
