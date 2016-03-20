from mock import ANY, call, Mock, patch
import os
import uuid

import cv2
from flask import current_app
from PIL import Image, ImageStat, ImageOps
import pytest

from admin.services import get_group_document
import analysis.services as ans
import camera.tests.test_services
from picture.services import build_picture_path
from thermal.appmodule import celery
from thermal.services import save_generic


class TestServicesIntegration(object):

    def test_get_image_mean_pixel_value_gets_correct_value(self):
        image_path = os.path.join(os.path.dirname(camera.tests.test_services.__file__),
                                  'fixtures',
                                  '3f4c4361-9a07-48a3-92a8-fda41f1be93e.jpg')
        mean_pixel_value = ans.get_image_mean_pixel_value(image_path)
        assert mean_pixel_value == 111.66625


class TestServicesUnit(object):


    @patch('analysis.services.get_document_with_exception')
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    def test_build_blurred_cv2_image_calls_right_methods(self,
                                                         cv2_gaussianblur,
                                                         cv2_cvtcolor,
                                                         cv2_imread,
                                                         as_get_document_with_exception):

        as_get_document_with_exception.return_value = {'uri': 'something_awful'}
        cv2_imread.return_value = 'greg'
        cv2_cvtcolor.return_value = 'peter' 
        cv2_gaussianblur.return_value = 'bobby'

        return_value = ans.build_blurred_cv2_image('123')

        as_get_document_with_exception.assert_called_once_with('123', 'picture')
        cv2_imread.assert_called_once_with('something_awful')
        cv2_cvtcolor.assert_called_once_with('greg', cv2.COLOR_BGR2GRAY)
        cv2_gaussianblur.assert_called_once_with('peter', (3,3), 0)
        assert return_value == 'bobby'

    def test_scale_image(self):
        class MockImage(object):
            pass

        group_id = uuid.uuid4()
        snap_id = uuid.uuid4()
        ans.save_generic = Mock()
        the_picture_path = build_picture_path(picture_name='whatever', snap_id=snap_id, create_directory=False)
        ans.get_document_with_exception = Mock(return_value={'filename': 'whatever',
                                                             'group_id': str(group_id),
                                                             'snap_id': str(snap_id),
                                                             'uri': the_picture_path})
        ans.get_group_document = Mock(return_value={'_id': str(group_id),
                                                    'colorize_range_low': 1.1,
                                                    'colorize_range_high': 2.2})
        the_mock_image = MockImage()
        Image.open = Mock(return_value=the_mock_image)
        MockImage.resize = Mock(return_value=the_mock_image)
        MockImage.save = Mock()
        ImageOps.colorize = Mock(return_value=the_mock_image)
        img_id_in = uuid.uuid4()
        img_id_out = uuid.uuid4()
        image_width = current_app.config['STILL_IMAGE_WIDTH']
        image_height = current_app.config['STILL_IMAGE_HEIGHT']
        img_filename_out = ans.build_picture_name(img_id_out)
        pic_path_out = ans.build_picture_path(picture_name=img_filename_out, snap_id=snap_id)
        test_img_dict_out = {
            '_id': str(img_id_out),
            'type': 'picture',
            'source': 'analysis',
            'source_image_id': str(img_id_in),
            'analysis_type': 'colorize_bicubic',
            'group_id': str(group_id),
            'snap_id': str(snap_id),
            'filename': img_filename_out,
            'uri': ANY,
            'created': ANY
        }

        ans.scale_image(img_id_in, img_id_out, 'whatever')

        ans.get_group_document.assert_called_once_with('whatever')
        ans.get_document_with_exception.assert_called_once_with(str(img_id_in), 'picture')
        Image.open.assert_called_once_with(ans.build_picture_path(picture_name='whatever', snap_id=snap_id))
        MockImage.resize.assert_called_once_with((image_width, image_height), Image.BICUBIC)
        ImageOps.colorize.assert_called_once_with(the_mock_image, 1.1, 2.2)
        MockImage.save.assert_called_once_with(pic_path_out)
        ans.save_generic.assert_called_once_with(test_img_dict_out, 'picture')


    @patch('analysis.services.get_image_mean_pixel_value')
    def test_check_if_image_is_too_dark_returns_true_if_image_is_too_dark(self,
                                                                          as_get_image_mean_pixel_value):
        as_get_image_mean_pixel_value.return_value = 50.0

        ret_val = ans.check_if_image_is_too_dark('whatever', 51)

        assert ret_val
        assert as_get_image_mean_pixel_value.called_once_with('whatever')

    @patch('analysis.services.get_image_mean_pixel_value')
    def test_check_if_image_is_too_dark_returns_false_if_image_is_not_too_dark(self,
                                                                               as_get_image_mean_pixel_value):
        as_get_image_mean_pixel_value.return_value = 50.0

        ret_val = ans.check_if_image_is_too_dark('whatever', 49)

        assert not ret_val
        assert as_get_image_mean_pixel_value.called_once_with('whatever')

        
    @patch('analysis.services.build_blurred_cv2_image')
    @patch('analysis.services.auto_canny')
    @patch('analysis.services.build_picture_name')
    @patch('analysis.services.build_picture_path')
    @patch('cv2.imwrite')
    @patch('analysis.services.make_edge_picture_dict')
    @patch('analysis.services.save_generic')
    def test_edge_detect_auto_calls_expected_methods(self,
                                                     as_save_generic,
                                                     as_make_edge_picture_dict,
                                                     cv2_imwrite,
                                                     as_build_picture_path,
                                                     as_build_picture_name,
                                                     as_auto_canny,
                                                     as_build_blurred_cv2_image):

        as_make_edge_picture_dict.return_value = 'paul_gleason'
        as_build_picture_path.return_value = 'anthony_michael_hall'
        as_build_picture_name.return_value = 'emilio_estevez'
        as_auto_canny.return_value = 'judd_nelson'
        as_build_blurred_cv2_image.return_value = 'molly_ringwald'

        dict_in = {'snap_id':'6464', 'group_id': '7373'}
        ans.edge_detect_auto('ali_baba', dict_in, 'seven_thieves')

        as_build_blurred_cv2_image.assert_called_once_with('ali_baba')
        as_auto_canny.assert_called_once_with('molly_ringwald')
        as_build_picture_name.assert_called_once_with('seven_thieves')
        as_build_picture_path.assert_called_once_with(picture_name='emilio_estevez', snap_id='6464')
        cv2_imwrite.assert_called_once_with('anthony_michael_hall', 'judd_nelson')
        as_make_edge_picture_dict.assert_called_once_with(pic_id='seven_thieves',
                                                          pic_filename='emilio_estevez',
                                                          pic_path='anthony_michael_hall',
                                                          snap_id='6464',
                                                          group_id='7373',
                                                          source_pic_id='ali_baba',
                                                          edge_detect_type='auto')
        as_save_generic.assert_called_once_with('paul_gleason', 'picture')


# test scale image with no colorize
# test scale image with bilinear
# test scale image with antialias
# test_scale_image_with_invalid_image_id
# test edge_detect with invalid image_id
# test edge_detect with a valid alternate_image_id
# test edge_detect with just a auto_id, no wide or tight
