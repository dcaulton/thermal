from mock import ANY, call, Mock, patch
import os
import uuid

import cv2
from flask import current_app
from PIL import Image, ImageFilter, ImageStat, ImageOps
import pytest

from admin.services import get_group_document
import analysis.services as ans
import camera.tests.test_services
from picture.services import build_picture_path
from thermal.appmodule import celery
from thermal.exceptions import ThermalBaseError
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


    @patch('analysis.services.get_group_document')
    @patch('analysis.services.get_document_with_exception')
    @patch('analysis.services.build_picture_name')
    @patch('analysis.services.build_picture_path')
    @patch('analysis.services.scale_image_subtask')
    def test_scale_image_accepts_scale_type_through_kwargs(self,
                                                           as_scale_image_subtask,
                                                           as_build_picture_path,
                                                           as_build_picture_name,
                                                           as_get_document_with_exception,
                                                           as_get_group_document):

        as_get_group_document.return_value = {'_id': 'd1'}
        as_scale_image_subtask.side_effect = ThermalBaseError('wocka_wocka')
        Image.open = Mock(return_value='ali_baba')
        as_build_picture_path.return_value = 'steve_mcnair'
        as_build_picture_name.return_value = 'mongo_mcmichael'
        as_get_document_with_exception.return_value = {'filename': 'a1', 'uri': 'b1', 'snap_id': 'c1'}

        with pytest.raises(ThermalBaseError) as exception_info:
            return_value = ans.scale_image('a', 'b', 'c', scale_type='specified_scale_type')
            
        as_scale_image_subtask.assert_called_once_with('specified_scale_type', ANY)

    @patch('analysis.services.get_group_document')
    @patch('analysis.services.get_document_with_exception')
    @patch('analysis.services.build_picture_name')
    @patch('analysis.services.build_picture_path')
    @patch('analysis.services.scale_image_subtask')
    def test_scale_image_accepts_scale_type_through_group_record(self,
                                                                 as_scale_image_subtask,
                                                                 as_build_picture_path,
                                                                 as_build_picture_name,
                                                                 as_get_document_with_exception,
                                                                 as_get_group_document):

        as_get_group_document.return_value = {'_id': 'd1', 'scale_type': 'group_scale_type'}
        as_scale_image_subtask.side_effect = ThermalBaseError('wocka_wocka')
        Image.open = Mock(return_value='ali_baba')
        as_build_picture_path.return_value = 'steve_mcnair'
        as_build_picture_name.return_value = 'mongo_mcmichael'
        as_get_document_with_exception.return_value = {'filename': 'a1', 'uri': 'b1', 'snap_id': 'c1'}

        with pytest.raises(ThermalBaseError) as exception_info:
            return_value = ans.scale_image('a', 'b', 'c')
            
        as_scale_image_subtask.assert_called_once_with('group_scale_type', ANY)


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

    @patch('analysis.services.build_blurred_cv2_image')
    @patch('cv2.Canny')
    @patch('analysis.services.build_picture_name')
    @patch('analysis.services.build_picture_path')
    @patch('cv2.imwrite')
    @patch('analysis.services.make_edge_picture_dict')
    @patch('analysis.services.save_generic')
    def test_edge_detect_with_canny_limits_calls_expected_methods(self,
                                                                  as_save_generic,
                                                                  as_make_edge_picture_dict,
                                                                  cv2_imwrite,
                                                                  as_build_picture_path,
                                                                  as_build_picture_name,
                                                                  as_cv2_canny,
                                                                  as_build_blurred_cv2_image):

        as_make_edge_picture_dict.return_value = 'paul_gleason'
        as_build_picture_path.return_value = 'anthony_michael_hall'
        as_build_picture_name.return_value = 'emilio_estevez'
        as_cv2_canny.return_value = 'judd_nelson'
        as_build_blurred_cv2_image.return_value = 'molly_ringwald'

        dict_in = {'snap_id':'6464', 'group_id': '7373'}
        ans.edge_detect_with_canny_limits('ali_baba', dict_in, 'seven_thieves', 111, 222)

        as_build_blurred_cv2_image.assert_called_once_with('ali_baba')
        as_cv2_canny.assert_called_once_with('molly_ringwald', 111, 222)
        as_build_picture_name.assert_called_once_with('seven_thieves')
        as_build_picture_path.assert_called_once_with(picture_name='emilio_estevez', snap_id='6464')
        cv2_imwrite.assert_called_once_with('anthony_michael_hall', 'judd_nelson')
        as_make_edge_picture_dict.assert_called_once_with(pic_id='seven_thieves',
                                                          pic_filename='emilio_estevez',
                                                          pic_path='anthony_michael_hall',
                                                          snap_id='6464',
                                                          group_id='7373',
                                                          source_pic_id='ali_baba',
                                                          edge_detect_type='custom:111-222')
        as_save_generic.assert_called_once_with('paul_gleason', 'picture')

    @patch('analysis.services.get_document_with_exception')
    @patch('analysis.services.edge_detect_auto')
    @patch('analysis.services.edge_detect_with_canny_limits')
    def test_edge_detect_calls_expected_methods_for_all(self,
                                                        as_edge_detect_with_canny_limits,
                                                        as_edge_detect_auto,
                                                        as_get_document_with_exception):
        as_get_document_with_exception.return_value = {'some': 'thing'}
        
        ans.edge_detect('123', detection_threshold='all')

        as_get_document_with_exception.assert_called_once_with('123', 'picture')
        as_edge_detect_auto.assert_called_once_with('123', {'some': 'thing'}, ANY)
        call_one = call('123', {'some': 'thing'}, ANY, 10, 200)
        call_two = call('123', {'some': 'thing'}, ANY, 225, 250)
        as_edge_detect_with_canny_limits.assert_has_calls([call_one, call_two])

    @patch('analysis.services.get_document_with_exception')
    @patch('analysis.services.edge_detect_auto')
    @patch('analysis.services.edge_detect_with_canny_limits')
    def test_edge_detect_calls_expected_methods_for_auto(self,
                                                         as_edge_detect_with_canny_limits,
                                                         as_edge_detect_auto,
                                                         as_get_document_with_exception):
        as_get_document_with_exception.return_value = {'some': 'thing'}
        
        ans.edge_detect('123', detection_threshold='auto')

        as_get_document_with_exception.assert_called_once_with('123', 'picture')
        as_edge_detect_auto.assert_called_once_with('123', {'some': 'thing'}, ANY)
        as_edge_detect_with_canny_limits.assert_not_called()

    @patch('analysis.services.get_document_with_exception')
    @patch('analysis.services.edge_detect_auto')
    @patch('analysis.services.edge_detect_with_canny_limits')
    def test_edge_detect_calls_expected_methods_for_wide(self,
                                                         as_edge_detect_with_canny_limits,
                                                         as_edge_detect_auto,
                                                         as_get_document_with_exception):
        as_get_document_with_exception.return_value = {'some': 'thing'}
        
        ans.edge_detect('123', detection_threshold='wide')

        as_get_document_with_exception.assert_called_once_with('123', 'picture')
        as_edge_detect_auto.assert_not_called()
        call_one = call('123', {'some': 'thing'}, ANY, 10, 200)
        as_edge_detect_with_canny_limits.assert_has_calls([call_one])

    @patch('analysis.services.get_document_with_exception')
    @patch('analysis.services.edge_detect_auto')
    @patch('analysis.services.edge_detect_with_canny_limits')
    def test_edge_detect_calls_expected_methods_for_tight(self,
                                                          as_edge_detect_with_canny_limits,
                                                          as_edge_detect_auto,
                                                          as_get_document_with_exception):
        as_get_document_with_exception.return_value = {'some': 'thing'}
        
        ans.edge_detect('123', detection_threshold='tight')

        as_get_document_with_exception.assert_called_once_with('123', 'picture')
        as_edge_detect_auto.assert_not_called()
        call_one = call('123', {'some': 'thing'}, ANY, 225, 250)
        as_edge_detect_with_canny_limits.assert_has_calls([call_one])


    def test_make_edge_picture_dict_makes_dict_with_expected_fields(self):
        the_dict = ans.make_edge_picture_dict(pic_id='a',
                                              pic_filename='b',
                                              pic_path='c',
                                              snap_id='d',
                                              group_id='e',
                                              source_pic_id='f',
                                              edge_detect_type='g')
        assert '_id' in the_dict
        assert the_dict['_id'] == 'a'
        assert 'type' in the_dict
        assert the_dict['type'] == 'picture'
        assert 'source' in the_dict
        assert the_dict['source'] == 'analysis'
        assert 'source_image_id' in the_dict
        assert the_dict['source_image_id'] == 'f'
        assert 'analysis_type' in the_dict
        assert the_dict['analysis_type'] == 'edge detect'
        assert 'edge_detect_type' in the_dict
        assert the_dict['edge_detect_type'] == 'g'
        assert 'group_id' in the_dict
        assert the_dict['group_id'] == 'e'
        assert 'snap_id' in the_dict
        assert the_dict['snap_id'] == 'd'
        assert 'filename' in the_dict
        assert the_dict['filename'] == 'b'
        assert 'uri' in the_dict
        assert the_dict['uri'] == 'c'
        assert 'created' in the_dict
        assert len(the_dict.keys()) == 11


    @patch('numpy.median')
    @patch('cv2.Canny')
    def test_auto_canny_calls_expected_methods(self,
                                               cv2_canny,
                                               np_median):
        np_median.return_value = 0.5
        cv2_canny.return_value = 'steve'
        
        return_value = ans.auto_canny('thing')

        np_median.assert_called_once_with('thing'), .67*5
        cv2_canny.assert_called_once_with('thing', 0, 0)
        assert return_value == 'steve'
  

    @patch('analysis.services.search_generic')
    def test_build_distortion_pair_strings_calls_expected_methods(self,
                                                                  as_search_generic):
        as_search_generic.return_value = [{'start_x': '56', 'start_y': '57', 'end_x': '58', 'end_y': '59'},
                                          {'start_x': '76', 'start_y': '77', 'end_x': '78', 'end_y': '79'}]

        return_value = ans.build_distortion_pair_strings('taffy')

        as_search_generic.assert_called_once_with(document_type='distortion_pair',
                                                  args_dict={'distortion_set_id': 'taffy'})
        assert return_value == ['56,57,58,59', '76,77,78,79']

    @patch('analysis.services.build_distortion_pair_strings')
    def test_build_command_string_calls_expected_methods(self,
                                                         as_build_distortion_pair_strings):
        as_build_distortion_pair_strings.return_value = ['mamasita', 'chile_relleno']

        return_value = ans.build_command_string('a', 'b', 'c')

        as_build_distortion_pair_strings.assert_called_once_with('a')

        # TODO for the moment I have hardcoded it but have this test flag when that hack goes away
        # assert return_value == "convert b -distort Shepards 'mamasita chile_relleno' c"
        assert return_value == "convert b -distort Shepards '300,110 350,140  600,310 650,340' c"

    @patch('analysis.services.log_asynchronous_exception')
    @patch('analysis.services.edge_detect')
    def test_edge_detect_chained_catches_exception(self,
                                                   as_edge_detect,
                                                   as_log_asynchronous_exception):
        the_exception = ThermalBaseError('donovan_mcnabb')
        as_edge_detect.side_effect = the_exception

        ans.edge_detect_chained('a', 'b', detection_threshold='c', auto_id='d', wide_id='e', tight_id='f')

        as_edge_detect.assert_called_once_with('b', 'c', 'd', 'e', 'f')
        as_log_asynchronous_exception.assert_called_once_with(the_exception)

    @patch('analysis.services.log_asynchronous_exception')
    @patch('analysis.services.edge_detect')
    def test_edge_detect_task_catches_exception(self,
                                                as_edge_detect,
                                                as_log_asynchronous_exception):
        the_exception = ThermalBaseError('trent_dilfer')
        as_edge_detect.side_effect = the_exception

        ans.edge_detect_task('a', detection_threshold='b', auto_id='c', wide_id='d', tight_id='e')

        as_edge_detect.assert_called_once_with('a', 'b', 'c', 'd', 'e')
        as_log_asynchronous_exception.assert_called_once_with(the_exception)

    @patch('analysis.services.log_asynchronous_exception')
    @patch('analysis.services.scale_image')
    def test_scale_image_chained_catches_exception(self,
                                                   as_scale_image,
                                                   as_log_asynchronous_exception):
        the_exception = ThermalBaseError('dante_culpepper')
        as_scale_image.side_effect = the_exception

        ans.scale_image_chained('a', 'b', 'c', 'd')

        as_scale_image.assert_called_once_with('b', 'c', 'd')
        as_log_asynchronous_exception.assert_called_once_with(the_exception)


    @patch('analysis.services.scale_image')
    def test_empty_scale_image_kwarg_suppresses_call_in_scale_image_chained(self,
                                                                            as_scale_image):
        ans.scale_image_chained('a', 'b', 'c', 'd', scale_image='')

        as_scale_image.assert_not_called()


    @patch('analysis.services.log_asynchronous_exception')
    @patch('analysis.services.scale_image')
    def test_scale_image_task_catches_exception(self,
                                                as_scale_image,
                                                as_log_asynchronous_exception):
        the_exception = ThermalBaseError('carlton_fisk')
        as_scale_image.side_effect = the_exception

        ans.scale_image_task('a', 'b', 'c')

        as_scale_image.assert_called_once_with('a', 'b', 'c')
        as_log_asynchronous_exception.assert_called_once_with(the_exception)

    @patch('analysis.services.log_asynchronous_exception')
    @patch('analysis.services.distort_image_shepards')
    def test_distort_image_shepards_chained_catches_exception(self,
                                                              as_distort_image_shepards,
                                                              as_log_asynchronous_exception):
        the_exception = ThermalBaseError('bo_jackson')
        as_distort_image_shepards.side_effect = the_exception

        ans.distort_image_shepards_chained('a', 'b', 'c')

        as_distort_image_shepards.assert_called_once_with(image_id_in='b', image_id_out='c', distortion_set_id=None)
        as_log_asynchronous_exception.assert_called_once_with(the_exception)

    @patch('analysis.services.log_asynchronous_exception')
    @patch('analysis.services.distort_image_shepards')
    def test_distort_image_shepards_task_catches_exception(self,
                                                           as_distort_image_shepards,
                                                           as_log_asynchronous_exception):
        the_exception = ThermalBaseError('matt_forte')
        as_distort_image_shepards.side_effect = the_exception

        ans.distort_image_shepards_task('a', 'b', 'c')

        as_distort_image_shepards.assert_called_once_with(image_id_in='a', image_id_out='b', distortion_set_id='c')
        as_log_asynchronous_exception.assert_called_once_with(the_exception)



    @patch('analysis.services.get_document_with_exception')
    @patch('analysis.services.build_picture_name')
    @patch('analysis.services.build_picture_path')
    @patch('analysis.services.build_command_string')
    @patch('os.system')
    @patch('analysis.services.save_generic')
    def test_distort_image_shepards_calls_expected_methods(self,
                                                           as_save_generic,
                                                           os_system,
                                                           as_build_command_string,
                                                           as_build_picture_path,
                                                           as_build_picture_name,
                                                           as_get_document_with_exception):

        as_get_document_with_exception.return_value = {'group_id': 'some_group_id',
                                                       'uri': 'the_uri',
                                                       'snap_id': 'some_snap_id'}
        as_build_picture_name.return_value = 'some_picture_name'
        as_build_picture_path.return_value = 'some_picture_path'
        as_build_command_string.return_value = 'the_command_string'

        ans.distort_image_shepards(image_id_in='img_id_in', image_id_out='img_id_out', distortion_set_id='dist_set_id')

        as_get_document_with_exception.assert_called_once_with('img_id_in', 'picture')
        as_build_picture_name.assert_called_once_with('img_id_out')
        as_build_picture_path.assert_called_once_with(picture_name='some_picture_name', snap_id='some_snap_id')
        as_build_command_string.assert_called_once_with('dist_set_id', 'the_uri', 'some_picture_path')
        os_system.assert_called_once_with('the_command_string')
        as_save_generic.assert_called_once_with({'_id': 'img_id_out',
                                                 'type': 'picture',
                                                 'source': 'analysis',
                                                 'source_image_id': 'img_id_in',
                                                 'analysis_type': 'distort',
                                                 'group_id': 'some_group_id',
                                                 'snap_id': 'some_snap_id',
                                                 'filename': 'some_picture_name',
                                                 'uri': 'some_picture_path',
                                                 'created': ANY}, 'picture')


    def test_scale_image_subtask_gets_right_value_for_bilinear(self):
        class MockImage(object):
            pass
        mock_image = MockImage()
        mock_image.resize = Mock(return_value = 'hey_ya')

        return_value = ans.scale_image_subtask('bilinear_algebra', mock_image)

        current_app_width = current_app.config['STILL_IMAGE_WIDTH']
        current_app_height = current_app.config['STILL_IMAGE_HEIGHT']

        mock_image.resize.assert_called_once_with((current_app_width, current_app_height), Image.BILINEAR)
        assert return_value == 'hey_ya'

    def test_scale_image_subtask_gets_right_value_for_antialias(self):
        class MockImage(object):
            pass
        mock_image = MockImage()
        mock_image.resize = Mock(return_value = 'hey_ya')

        return_value = ans.scale_image_subtask('batman_antialias', mock_image)

        current_app_width = current_app.config['STILL_IMAGE_WIDTH']
        current_app_height = current_app.config['STILL_IMAGE_HEIGHT']

        mock_image.resize.assert_called_once_with((current_app_width, current_app_height), Image.ANTIALIAS)
        assert return_value == 'hey_ya'

    def test_colorize_image_returns_image_unchange_when_colorize_not_requested(self):
        return_value = ans.colorize_image('something_boring', {}, 'some_image')
        assert return_value == 'some_image'

    def test_blur_image_blurs_image_nine_times(self):
        class MockImage(object):
            pass
        mock_image = MockImage()
        mock_image.filter = Mock(return_value=mock_image)

        return_value = ans.blur_image('blurry_thing', mock_image)

        mock_image.filter.assert_has_calls([call(ImageFilter.BLUR),
                                            call(ImageFilter.BLUR),
                                            call(ImageFilter.BLUR),
                                            call(ImageFilter.BLUR),
                                            call(ImageFilter.BLUR),
                                            call(ImageFilter.BLUR),
                                            call(ImageFilter.BLUR),
                                            call(ImageFilter.BLUR),
                                            call(ImageFilter.BLUR)])
