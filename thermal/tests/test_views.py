import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

from flask import current_app

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

    @patch('thermal.views.search_generic')
    def test_generic_list_view_calls_search_generic(self,
                                                    av_find_groups):
        tv_search_generic.side_effect.return_value = {'1212': {'_id': '1212'},
                                                      '2323': {'_id': '2323'}}
        resp_object = tv.generic_list_view(document_type='something')
        tv.generic_list_view.assert_called_once_with(document_type='something')
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
