import json
from mock import ANY, call, Mock, patch
import uuid

from flask import current_app, request

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


    def test_get_delay_parameter_fetches_delay_parameter(self):
        with current_app.test_request_context('/whatever?delay=657'):
            from flask import request  # I know, crazy, but you need to import request here, not at the top of the module
            assert 'delay' in request.args
            delay = cv.get_delay_parameter()
            assert delay == 657


    def test_get_delay_parameter_defaults_to_0(self):
        with current_app.test_request_context('/whatever'):
            delay = cv.get_delay_parameter()
            assert delay == 0


    def test_get_repeat_parameter_fetches_repeat_parameter(self):
        with current_app.test_request_context('/whatever?repeat=8'):
            from flask import request
            assert 'repeat' in request.args
            repeat = cv.get_repeat_parameter()
            assert repeat == 8


    def test_get_repeat_parameter_defaults_to_0(self):
        with current_app.test_request_context('/whatever'):
            repeat = cv.get_repeat_parameter()
            assert repeat == 0


    def test_get_scale_image_parameter_casts_scale_image_parameter_to_true(self):
        with current_app.test_request_context('/whatever?scale_image=yipee'):
            from flask import request
            assert 'scale_image' in request.args
            scale_image = cv.get_scale_image_parameter()
            assert scale_image


    def test_get_scale_image_parameter_defaults_to_true(self):
        with current_app.test_request_context('/whatever'):
            scale_image = cv.get_scale_image_parameter()
            assert scale_image


    def test_get_scale_image_parameter_can_be_suppressed_with_empty_string(self):
        with current_app.test_request_context('/whatever?scale_image='):
            from flask import request
            assert 'scale_image' in request.args
            scale_image = cv.get_scale_image_parameter()
            assert not scale_image
