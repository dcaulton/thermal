import json
from mock import ANY, call, Mock, patch
import pytest

from flask import current_app

import calibration.views as cv
from thermal.utils import get_document


class TestViewsUnit(object):


    @patch('calibration.views.get_url_base')
    def test_index_shows_links(self, av_get_url_base):
        av_get_url_base.return_value = 'grouper'
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/calibration/')

            response_data_dict = json.loads(resp_object.data)

            assert resp_object.status_code == 200
            assert 'distortion_sets' in response_data_dict
            assert 'grouper' in response_data_dict['distortion_sets']
            assert 'distortion_pairs' in response_data_dict
            assert 'grouper' in response_data_dict['distortion_pairs']
            assert 'calibration_sessions' in response_data_dict
            assert 'grouper' in response_data_dict['calibration_sessions']
            assert len(response_data_dict.keys()) == 3
            av_get_url_base.assert_called_once_with()


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
    @patch('calibration.views.item_exists')
    def test_create_distortion_pair_calls_generic_save_view(self,
                                                           cv_item_exists,
                                                           cv_generic_save_view):


        cv_item_exists.return_value = True
        with current_app.test_request_context('/whatever',
                                              headers={'Content-Type':'application/json'},
                                              data='{"distortion_set_id":"umma_gumma", "start_x": "55"}'):
            resp_object = cv.create_distortion_pair()
            cv_item_exists.assert_called_once_with('umma_gumma', 'distortion_set')
            cv_generic_save_view.assert_called_once_with(document_type='distortion_pair')

    @patch('calibration.views.generic_save_view')
    @patch('calibration.views.item_exists')
    def test_create_distortion_pair_generates_distortion_set_id_if_none_provided(self,
                                                                                 cv_item_exists,
                                                                                 cv_generic_save_view):


        cv_item_exists.return_value = True
        with current_app.test_request_context('/whatever',
                                              headers={'Content-Type':'application/json'},
                                              data='{"start_x": "55"}'):
            resp_object = cv.create_distortion_pair()
            cv_item_exists.assert_called_once_with(ANY, 'distortion_set')
            cv_generic_save_view.assert_called_once_with(document_type='distortion_pair')


    @patch('calibration.views.generic_save_view')
    @patch('calibration.views.save_generic')
    @patch('calibration.views.item_exists')
    def test_create_distortion_pair_uses_existing_distortion_set_id_if_none_provided_and_creates_one(self,
                                                                                                     cv_item_exists,
                                                                                                     cv_save_generic,
                                                                                                     cv_generic_save_view):


        cv_item_exists.return_value = False
        with current_app.test_request_context('/whatever',
                                              headers={'Content-Type':'application/json'},
                                              data='{"distortion_set_id":"umma_gumma", "start_x": "55"}'):
            resp_object = cv.create_distortion_pair()
            cv_item_exists.assert_called_once_with('umma_gumma', 'distortion_set')
            cv_save_generic.assert_called_once_with({'_id': 'umma_gumma', 'type': 'distortion_set'}, 
                                                    'distortion_set')
            cv_generic_save_view.assert_called_once_with(document_type='distortion_pair')


    @patch('calibration.views.generic_save_view')
    def test_create_calibration_session_calls_generic_save_view(self,
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
