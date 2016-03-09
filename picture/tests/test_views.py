import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

from flask import current_app, Response

import picture.views as pv
from thermal.exceptions import NotFoundError


class TestViewsUnit(object):

    @patch('picture.views.get_document_with_exception')
    def test_get_picture_calls_get_document_with_exception_method(self,
                                                                  pv_get_document_with_exception):
        pv_get_document_with_exception.return_value = {'e': 'd'}

        resp_object = pv.get_picture('4231')
        response_data_dict = json.loads(resp_object.data)

        pv_get_document_with_exception.assert_called_once_with('4231', 'picture')
        assert resp_object.status_code == 200
        assert 'e' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('picture.views.get_document_with_exception')
    def test_get_picture_fails_as_expected(self,
                                           pv_get_document_with_exception):
        pv_get_document_with_exception.side_effect = NotFoundError('no picture there, friend')

        resp_object = pv.get_picture('4231')
        response_data_dict = json.loads(resp_object.data)

        pv_get_document_with_exception.assert_called_once_with('4231', 'picture')
        assert resp_object.status_code == 404
        assert resp_object.data == '"no picture there, friend"'

    @patch('picture.views.generic_list_view')
    def test_list_pictures_calls_generic_list_view(self,
                                                   pv_generic_list_view):
        pv_generic_list_view.return_value = {'6767': {'_id': '6767'},
                                             '7878': {'_id': '7878'}}
    
        resp_object = pv.list_pictures()

        pv_generic_list_view.assert_called_once_with(document_type='picture')
