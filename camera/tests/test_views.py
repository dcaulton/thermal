import json
from mock import ANY, call, Mock, patch
import uuid

from flask import current_app, request

import camera.views as cv
from thermal.exceptions import ThermalBaseError


class TestViewsUnit(object):

    @patch('camera.views.get_url_base')
    def test_index_shows_links(self, cv_get_url_base):
        cv_get_url_base.return_value = 'grouper'
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/camera/')

            response_data_dict = json.loads(resp_object.data)

            assert resp_object.status_code == 200
            assert 'picam_still' in response_data_dict
            assert 'grouper' in response_data_dict['picam_still']
            assert 'thermal_still' in response_data_dict
            assert 'grouper' in response_data_dict['thermal_still']
            assert 'both_still' in response_data_dict
            assert 'grouper' in response_data_dict['both_still']
            assert len(response_data_dict.keys()) == 3
            cv_get_url_base.assert_called_once_with()

    @patch('camera.views.take_picam_still')
    @patch('camera.views.gather_and_enforce_request_args')
    @patch('camera.views.get_settings_document')
    def test_picam_still_no_delay_or_repeat_calls_appropriate_methods(self,
                                                                      cv_get_settings_document,
                                                                      cv_gather_and_enforce_request_args,
                                                                      cv_take_picam_still):
        group_id = uuid.uuid4()
        cv_get_settings_document.return_value = {'current_group_id': group_id}
        cv_gather_and_enforce_request_args.return_value = {'delay': 54, 'repeat': 32}
        cv_take_picam_still.return_value = {'a': 'b'}

        resp_object = cv.picam_still()
        response_data_dict = json.loads(resp_object.data)

        cv_get_settings_document.assert_called_once_with()
        cv_gather_and_enforce_request_args.assert_called_once_with(ANY)
        cv_take_picam_still.assert_called_once_with(snap_id=ANY, group_id=group_id, delay=54, repeat=32)
        assert resp_object.status_code == 202
        assert 'a' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('camera.views.get_settings_document')
    def test_picam_still_catches_exceptions(self,
                                            cv_get_settings_document):

        cv_get_settings_document.side_effect = ThermalBaseError('gruyere')

        resp_object = cv.picam_still()
        assert resp_object.data == '"gruyere"'
        assert resp_object.status_code == 400

    @patch('camera.views.take_thermal_still')
    @patch('camera.views.gather_and_enforce_request_args')
    @patch('camera.views.get_settings_document')
    def test_thermal_still_no_delay_or_repeat_calls_appropriate_methods(self,
                                                                        cv_get_settings_document,
                                                                        cv_gather_and_enforce_request_args,
                                                                        cv_take_thermal_still):
        group_id = uuid.uuid4()
        cv_get_settings_document.return_value = {'current_group_id': group_id}
        cv_gather_and_enforce_request_args.return_value = {'delay': 28, 'repeat': 37, 'scale_image': True}
        cv_take_thermal_still.return_value = {'c': 'd'}

        resp_object = cv.thermal_still()
        response_data_dict = json.loads(resp_object.data)

        cv_get_settings_document.assert_called_once_with()
        cv_gather_and_enforce_request_args.assert_called_once_with(ANY)
        cv_take_thermal_still.assert_called_once_with(snap_id=ANY, group_id=group_id, delay=28, repeat=37, scale_image=True)
        assert resp_object.status_code == 202
        assert 'c' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('camera.views.get_settings_document')
    def test_thermal_still_catches_exceptions(self,
                                              cv_get_settings_document):

        cv_get_settings_document.side_effect = ThermalBaseError('emmenthaler')

        resp_object = cv.thermal_still()
        assert resp_object.data == '"emmenthaler"'
        assert resp_object.status_code == 400

    @patch('camera.views.take_both_still')
    @patch('camera.views.gather_and_enforce_request_args')
    @patch('camera.views.get_settings_document')
    def test_both_still_no_delay_or_repeat_calls_appropriate_methods(self,
                                                                     cv_get_settings_document,
                                                                     cv_gather_and_enforce_request_args,
                                                                     cv_take_both_still):
        group_id = uuid.uuid4()
        cv_get_settings_document.return_value = {'current_group_id': group_id}
        cv_gather_and_enforce_request_args.return_value = {'delay': 47, 'repeat': 56}
        cv_take_both_still.return_value = {'e': 'f'}

        resp_object = cv.both_still()
        response_data_dict = json.loads(resp_object.data)

        cv_get_settings_document.assert_called_once_with()
        cv_gather_and_enforce_request_args.assert_called_once_with(ANY)
        cv_take_both_still.assert_called_once_with(snap_id=ANY, group_id=group_id, delay=47, repeat=56)
        assert resp_object.status_code == 202
        assert 'e' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('camera.views.get_settings_document')
    def test_both_still_catches_exceptions(self,
                                           cv_get_settings_document):

        cv_get_settings_document.side_effect = ThermalBaseError('gouda')

        resp_object = cv.both_still()
        assert resp_object.data == '"gouda"'
        assert resp_object.status_code == 400
