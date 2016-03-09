import json
from mock import ANY, call, Mock, patch
import pytest

import picture.views as pv


class TestViewsUnit(object):

    @patch('picture.views.generic_get_view')
    def test_get_picture_calls_generic_get_view(self,
                                                pv_generic_get_view):
        pv_generic_get_view.return_value = {'6767': {'_id': '6767'},
                                            '7878': {'_id': '7878'}}
    
        resp_object = pv.get_picture('hooha')

        pv_generic_get_view.assert_called_once_with(item_id='hooha', document_type='picture')

    @patch('picture.views.generic_list_view')
    def test_list_pictures_calls_generic_list_view(self,
                                                   pv_generic_list_view):
        pv_generic_list_view.return_value = {'6767': {'_id': '6767'},
                                             '7878': {'_id': '7878'}}
    
        resp_object = pv.list_pictures()

        pv_generic_list_view.assert_called_once_with(document_type='picture')
