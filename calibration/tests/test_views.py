import json
from mock import ANY, call, Mock, patch
import pytest

import calibration.views as cv


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
