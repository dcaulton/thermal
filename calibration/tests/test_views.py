import json
from mock import ANY, call, Mock, patch
import pytest

from flask import current_app

import calibration.views as cv
from thermal.utils import get_document


class TestViewsUnit(object):

    @patch('calibration.views.generic_list_view')
    def test_list_distortion_sets_calls_generic_list_view(self,
                                                          cv_generic_list_view):
        cv_generic_list_view.return_value = {'6767': {'_id': '6767'},
                                             '7878': {'_id': '7878'}}
    
        resp_object = cv.list_distortion_sets()

        cv_generic_list_view.assert_called_once_with(document_type='distortion_set')

    @patch('calibration.views.generic_list_view')
    def test_list_distortion_pairs_calls_generic_list_view(self,
                                                           cv_generic_list_view):
        cv_generic_list_view.return_value = {'6767': {'_id': '6767'},
                                             '7878': {'_id': '7878'}}
    
        resp_object = cv.list_distortion_pairs()

        cv_generic_list_view.assert_called_once_with(document_type='distortion_pair')

    @patch('calibration.views.generic_list_view')
    def test_list_calibration_sessions_calls_generic_list_view(self,
                                                               cv_generic_list_view):
        cv_generic_list_view.return_value = {'6767': {'_id': '6767'},
                                             '7878': {'_id': '7878'}}
    
        resp_object = cv.list_calibration_sessions()

        cv_generic_list_view.assert_called_once_with(document_type='calibration_session')

    @patch('calibration.views.generic_get_view')
    def test_get_distortion_set_calls_generic_get_view(self,
                                                       cv_generic_get_view):
        resp_object = cv.get_distortion_set('hooha')

        cv_generic_get_view.assert_called_once_with(item_id='hooha', document_type='distortion_set')

    @patch('calibration.views.generic_get_view')
    def test_get_distortion_pair_calls_generic_get_view(self,
                                                        cv_generic_get_view):
        resp_object = cv.get_distortion_pair('hooha')

        cv_generic_get_view.assert_called_once_with(item_id='hooha', document_type='distortion_pair')

    @patch('calibration.views.generic_get_view')
    def test_get_calibration_session_calls_generic_get_view(self,
                                                            cv_generic_get_view):
        resp_object = cv.get_calibration_session('hooha')

        cv_generic_get_view.assert_called_once_with(item_id='hooha', document_type='calibration_session')

    @patch('calibration.views.generic_save_view')
    def test_create_distortion_set_calls_generic_save_view(self,
                                                       cv_generic_save_view):
        resp_object = cv.create_distortion_set()

        cv_generic_save_view.assert_called_once_with(document_type='distortion_set')

    @patch('calibration.views.generic_save_view')
    def test_get_distortion_pair_calls_generic_get_view(self,
                                                        cv_generic_save_view):
        resp_object = cv.create_distortion_pair()

        cv_generic_save_view.assert_called_once_with(document_type='distortion_pair')

    @patch('calibration.views.generic_save_view')
    def test_get_calibration_session_calls_generic_get_view(self,
                                                            cv_generic_save_view):
        resp_object = cv.create_calibration_session()

        cv_generic_save_view.assert_called_once_with(document_type='calibration_session')

class TestViewsIntegration(object):

    def test_generic_save_view_gets_args_from_create_distortion_pair_request_data(self):
        with current_app.test_client() as c:
            resp_object = c.post('/api/v1/calibration/distortion_pairs',
                                 headers={'Content-Type':'application/json'},
                                 data='{"thermo":"plastic"}')
            assert resp_object.status_code == 200

            doc_id = json.loads(resp_object.data)['_id']
            distortion_pair_document = get_document(doc_id)
            assert 'thermo' in distortion_pair_document
