import os
import uuid

from flask import current_app
from mock import ANY, call, Mock, patch
import pytest

import calibration.services as cs


class TestServicesUnit(object):


    @patch('calibration.services.get_documents_from_criteria')
    def test_find_distortion_sets_calls_expected_functions(self,
                                                           cs_get_documents_from_criteria):
        cs_get_documents_from_criteria.return_value = 'meh'
        return_val = cs.find_distortion_sets({'sponge': 'bob'})
        cs_get_documents_from_criteria.assert_called_once_with({'sponge': 'bob', 'type': 'distortion_set'})
        assert return_val == 'meh'

    @patch('calibration.services.get_documents_from_criteria')
    def test_find_distortion_pairs_calls_expected_functions(self,
                                                            cs_get_documents_from_criteria):
        cs_get_documents_from_criteria.return_value = 'meh'
        return_val = cs.find_distortion_pairs({'sponge': 'bob'})
        cs_get_documents_from_criteria.assert_called_once_with({'sponge': 'bob', 'type': 'distortion_pair'})
        assert return_val == 'meh'

    @patch('calibration.services.get_documents_from_criteria')
    def test_find_calibration_sessions_calls_expected_functions(self,
                                                                cs_get_documents_from_criteria):
        cs_get_documents_from_criteria.return_value = 'meh'
        return_val = cs.find_calibration_sessions({'sponge': 'bob'})
        cs_get_documents_from_criteria.assert_called_once_with({'sponge': 'bob', 'type': 'calibration_session'})
        assert return_val == 'meh'

    @patch('calibration.services.get_document_with_exception')
    def test_get_distortion_set_document_calls_expected_functions(self,
                                                                  cs_get_document_with_exception):
        cs_get_document_with_exception.return_value = {'whatevs': 'dont_care'}
        return_val = cs.get_distortion_set_document('jibba_jabba')
        cs_get_document_with_exception.assert_called_once_with('jibba_jabba', document_type='distortion_set')
        assert return_val == {'whatevs': 'dont_care'}

    @patch('calibration.services.get_document_with_exception')
    def test_get_distortion_pair_document_calls_expected_functions(self,
                                                                   cs_get_document_with_exception):
        cs_get_document_with_exception.return_value = {'whatevs': 'dont_care'}
        return_val = cs.get_distortion_pair_document('jibba_jabba')
        cs_get_document_with_exception.assert_called_once_with('jibba_jabba', document_type='distortion_pair')
        assert return_val == {'whatevs': 'dont_care'}

    @patch('calibration.services.get_document_with_exception')
    def test_get_calibration_session_document_calls_expected_functions(self,
                                                                       cs_get_document_with_exception):
        cs_get_document_with_exception.return_value = {'whatevs': 'dont_care'}
        return_val = cs.get_calibration_session_document('jibba_jabba')
        cs_get_document_with_exception.assert_called_once_with('jibba_jabba', document_type='calibration_session')
        assert return_val == {'whatevs': 'dont_care'}

