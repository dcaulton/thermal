from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
from PIL import Image, ImageChops
import pytest

from admin.services import get_group_document
import merging.services as ms
from thermal.appmodule import celery


class TestServicesUnit(object):

    def test_merge_images_with_primary_image(self):

        class MockImage(object):
            pass

        group_id = uuid.uuid4()
        snap_id = uuid.uuid4()
        ms.save_generic = Mock()
        ms.get_document_with_exception = Mock(return_value={'filename': 'whatever',
                                                             'group_id': str(group_id),
                                                             'snap_id': str(snap_id)})
        ms.get_group_document = Mock(return_value={'_id': str(group_id), 'merge_type': 'canine'})
        ms.item_exists = Mock(return_value=False)
        the_mock_image = MockImage()
        Image.open = Mock(return_value=the_mock_image)
        MockImage.convert = Mock(return_value=the_mock_image)
        MockImage.save = Mock()
        ImageChops.canine = Mock(return_value=the_mock_image)
        img1_primary_id_in = uuid.uuid4()
        img1_primary_filename_in = 'whatever'
        img1_primary_path_in = ms.build_picture_path(picture_name=img1_primary_filename_in, snap_id=snap_id)
        img1_alternate_id_in = uuid.uuid4()
        img2_id_in = uuid.uuid4()
        img2_filename_in = 'whatever'
        img2_path_in = ms.build_picture_path(picture_name=img2_filename_in, snap_id=snap_id)
        img_id_out = uuid.uuid4()
        img_filename_out = ms.build_picture_name(img_id_out)
        pic_path_out = ms.build_picture_path(picture_name=img_filename_out, snap_id=snap_id)
        test_img_dict_out = {
            '_id': str(img_id_out),
            'type': 'picture',
            'source': 'merge',
            'source_image_id_1': str(img1_primary_id_in),
            'source_image_id_2': str(img2_id_in),
            'merge_type': 'canine',
            'group_id': str(group_id),
            'snap_id': str(snap_id),
            'filename': img_filename_out,
            'uri': ANY,
            'created': ANY
        }

        ms.merge_images(img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out, group_id)

        ms.get_group_document.assert_called_once_with(group_id)
        ms.item_exists.assert_called_once_with(img1_alternate_id_in, 'picture')
        get_document_with_exception_calls = [call(str(img1_primary_id_in), 'picture'), call(str(img2_id_in), 'picture')]
        ms.get_document_with_exception.assert_has_calls(get_document_with_exception_calls)
        image_open_calls = [call(img1_primary_path_in), call(img2_path_in)]
        Image.open.assert_has_calls(image_open_calls)
        convert_calls = [call('RGBA'), call('RGBA')]
        MockImage.convert.assert_has_calls(convert_calls)
        ImageChops.canine.assert_called_once_with(the_mock_image, the_mock_image)
        MockImage.save.assert_called_once_with(pic_path_out)
        ms.save_generic.assert_called_once_with(test_img_dict_out, 'picture')
