import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

from flask import current_app

from thermal.exceptions import NotFoundError, ThermalBaseError
import thermal.views as tv


class TestViewsUnit(object):

    def test_index_shows_links(self):
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/')

            response_data_dict = json.loads(resp_object.data)

            assert resp_object.status_code == 200
            assert 'admin' in response_data_dict
            assert 'pictures' in response_data_dict
            assert 'analysis' in response_data_dict
            assert 'merging' in response_data_dict
            assert 'camera' in response_data_dict
            assert 'docs' in response_data_dict
            assert 'calibration' in response_data_dict
            assert len(response_data_dict.keys()) == 7

# TODO test_generic_list_view_does_paging    
# TODO test_generic_list_view_finds_parameters_from_request_args
# TODO test_generic_list_view_finds_parameters_from_args_dict
    @patch('thermal.views.search_generic')
    def test_generic_list_view_calls_search_generic(self,
                                                    tv_search_generic):
        tv_search_generic.return_value = {'1212': {'_id': '1212'},
                                          '2323': {'_id': '2323'}}
        resp_object = tv.generic_list_view(document_type='something')
        tv.search_generic.assert_called_once_with(document_type='something')
        response_data_dict = json.loads(resp_object.data)
        assert resp_object.status_code == 200
        assert '1212' in response_data_dict
        assert '2323' in response_data_dict
        assert len(response_data_dict.keys()) == 2

    @patch('thermal.views.search_generic')
    def test_generic_list_view_catches_exceptions(self,
                                                  tv_search_generic):

        tv_search_generic.side_effect = ThermalBaseError('phenomenon')

        resp_object = tv.generic_list_view(document_type='picture')
        assert resp_object.data == '"phenomenon"'
        assert resp_object.status_code == 400

    @patch('thermal.views.get_document_with_exception')
    def test_generic_get_view_calls_get_document_with_exception_method(self,
                                                                       tv_get_document_with_exception):
        tv_get_document_with_exception.return_value = {'e': 'd'}

        resp_object = tv.generic_get_view(item_id='4231', document_type='dirty_look')
        response_data_dict = json.loads(resp_object.data)

        tv_get_document_with_exception.assert_called_once_with('4231', 'dirty_look')
        assert resp_object.status_code == 200
        assert 'e' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('thermal.views.get_document_with_exception')
    def test_generic_get_view_fails_as_expected(self,
                                                tv_get_document_with_exception):
        tv_get_document_with_exception.side_effect = NotFoundError('no picture there, friend')

        resp_object = tv.generic_get_view(item_id='4231', document_type='misunderstanding')
        response_data_dict = json.loads(resp_object.data)

        tv_get_document_with_exception.assert_called_once_with('4231', 'misunderstanding')
        assert resp_object.status_code == 404
        assert resp_object.data == '"no picture there, friend"'
