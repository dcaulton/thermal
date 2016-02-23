import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

import picture.views as pv
from thermal.exceptions import NotFoundError


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


# TODO make a unit test when I figure out how to mock out the request headers and request.json.keys
# @picture.route('/')
# def list_pictures():
#     search_dict = {}
#     for key in request.args.keys():
#         search_dict[key] = request.args[key]
#     pictures = find_pictures(search_dict)
#      return Response(json.dumps(pictures), status=200, mimetype='application/json')
