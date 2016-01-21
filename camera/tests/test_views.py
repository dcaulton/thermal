import json
from mock import ANY, call, Mock, patch
import uuid

import camera.views as cv


class TestViewsUnit(object):

    @patch('camera.views.take_picam_still')
    @patch('camera.views.get_repeat_parameter')
    @patch('camera.views.get_delay_parameter')
    @patch('camera.views.get_settings_document')
    def test_picam_still_no_delay_or_repeat_calls_appropriate_methods(self,
                                                                      cv_get_settings_document,
                                                                      cv_get_delay_parameter,
                                                                      cv_get_repeat_parameter,
                                                                      cv_take_picam_still):
        group_id = uuid.uuid4()
        cv_get_settings_document.return_value = {'current_group_id': group_id}
        cv_get_delay_parameter.return_value = 54
        cv_get_repeat_parameter.return_value = 32
        cv_take_picam_still.return_value = {'a': 'b'}

        resp_object = cv.picam_still()
        response_data_dict = json.loads(resp_object.data)
    
        cv_get_settings_document.assert_called_once_with()
        cv_get_delay_parameter.assert_called_once_with()
        cv_get_repeat_parameter.assert_called_once_with()
        cv_take_picam_still.assert_called_once_with(snap_id=ANY, group_id=group_id, delay=54, repeat=32)
        assert resp_object.status_code == 202
        assert 'a' in response_data_dict
        assert len(response_data_dict.keys()) == 1


    @patch('camera.views.take_thermal_still')
    @patch('camera.views.get_scale_image_parameter')
    @patch('camera.views.get_repeat_parameter')
    @patch('camera.views.get_delay_parameter')
    @patch('camera.views.get_settings_document')
    def test_thermal_still_no_delay_or_repeat_calls_appropriate_methods(self,
                                                                        cv_get_settings_document,
                                                                        cv_get_delay_parameter,
                                                                        cv_get_repeat_parameter,
                                                                        cv_get_scale_image_parameter,
                                                                        cv_take_thermal_still):
        group_id = uuid.uuid4()
        cv_get_settings_document.return_value = {'current_group_id': group_id}
        cv_get_delay_parameter.return_value = 28
        cv_get_repeat_parameter.return_value = 37
        cv_get_scale_image_parameter.return_value = True
        cv_take_thermal_still.return_value = {'c': 'd'}

        resp_object = cv.thermal_still()
        response_data_dict = json.loads(resp_object.data)
    
        cv_get_settings_document.assert_called_once_with()
        cv_get_delay_parameter.assert_called_once_with()
        cv_get_repeat_parameter.assert_called_once_with()
        cv_get_scale_image_parameter.assert_called_once_with()
        cv_take_thermal_still.assert_called_once_with(snap_id=ANY, group_id=group_id, delay=28, repeat=37, scale_image=True)
        assert resp_object.status_code == 202
        assert 'c' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('camera.views.take_both_still')
    @patch('camera.views.get_repeat_parameter')
    @patch('camera.views.get_delay_parameter')
    @patch('camera.views.get_settings_document')
    def test_both_still_no_delay_or_repeat_calls_appropriate_methods(self,
                                                                        cv_get_settings_document,
                                                                        cv_get_delay_parameter,
                                                                        cv_get_repeat_parameter,
                                                                        cv_take_both_still):
        group_id = uuid.uuid4()
        cv_get_settings_document.return_value = {'current_group_id': group_id}
        cv_get_delay_parameter.return_value = 47
        cv_get_repeat_parameter.return_value = 56
        cv_take_both_still.return_value = {'e': 'f'}

        resp_object = cv.both_still()
        response_data_dict = json.loads(resp_object.data)
    
        cv_get_settings_document.assert_called_once_with()
        cv_get_delay_parameter.assert_called_once_with()
        cv_get_repeat_parameter.assert_called_once_with()
        cv_take_both_still.assert_called_once_with(snap_id=ANY, group_id=group_id, delay=47, repeat=56)
        assert resp_object.status_code == 202
        assert 'e' in response_data_dict
        assert len(response_data_dict.keys()) == 1
