import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

from flask import current_app

import picture.views as pv
from thermal.exceptions import NotFoundError, ThermalBaseError


class TestViewsUnit(object):

    @patch('picture.views.find_picture')
    def test_get_picture_calls_find_picture_method(self,
                                                   pv_find_picture):
        pv_find_picture.return_value = {'e': 'd'}

        resp_object = pv.get_picture('4231')
        response_data_dict = json.loads(resp_object.data)

        pv_find_picture.assert_called_once_with('4231')
        assert resp_object.status_code == 200
        assert 'e' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('picture.views.find_picture')
    def test_get_picture_fails_as_expected(self,
                                           pv_find_picture):
        pv_find_picture.side_effect = NotFoundError('no picture there, friend')

        resp_object = pv.get_picture('4231')
        response_data_dict = json.loads(resp_object.data)

        pv_find_picture.assert_called_once_with('4231')
        assert resp_object.status_code == 404
        assert resp_object.data == '"no picture there, friend"'


    @patch('picture.views.find_pictures')
    def test_list_pictures_matches_pictures_on_search_param(self,
                                                            pv_find_pictures):
        pv_find_pictures.return_value = {'6767': {'_id': '6767'},
                                         '7878': {'_id': '7878'}}
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/pictures/?food=rutabega')
            pv_find_pictures.assert_called_once_with({'food': 'rutabega'})
            response_data_dict = json.loads(resp_object.data)
            assert resp_object.status_code == 200
            assert '6767' in response_data_dict
            assert '7878' in response_data_dict
            assert len(response_data_dict.keys()) == 2

    @patch('picture.views.gather_and_enforce_request_args')
    def test_list_pictures_catches_exceptions(self,
                                              pv_gather_and_enforce_request_args):

        pv_gather_and_enforce_request_args.side_effect = ThermalBaseError('phenomenon')

        resp_object = pv.list_pictures()
        assert resp_object.data == '"phenomenon"'
        assert resp_object.status_code == 400
