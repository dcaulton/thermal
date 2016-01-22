import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

import admin.views as av
from thermal.exceptions import DocumentConfigurationError, NotFoundError


#TODO this needs a ton more tests
class TestViewsUnit(object):

    @patch('admin.views.get_settings_document')
    def test_get_settings_calls_get_settings_document(self,
                                                      av_get_settings_document):
        av_get_settings_document.return_value = {'h': 't'}

        resp_object = av.get_settings()
        response_data_dict = json.loads(resp_object.data)

        av_get_settings_document.assert_called_once_with()
        assert resp_object.status_code == 200
        assert 'h' in response_data_dict
        assert len(response_data_dict.keys()) == 1

#TODO test update_settings

#    @patch('admin.views.save_document')
#    @patch('admin.views.get_settings_document')
#    def test_update_settings_calls_all_methods(self,
#                                               av_get_settings_document,
#                                               av_save_document):
#        av_get_settings_document.return_value = {'x': 'y'}
#
#        tt = current_app.put('/admin/settings',
#                             data={'poker': 'face'},
#                             headers={'Content-Type': 'application/json'});
#
#        av_get_settings_document.assert_called_once_with()
#        av_save_document.assert_called_once_with({'x': 'y'})
#        assert resp_object.status_code == 200
#        assert 'h' in response_data_dict
#        assert len(response_data_dict.keys()) == 1
#
#test a doc attribute that cant be set

#@admin.route('/settings', methods=['PUT'])
#def update_settings():
#    settings = get_settings_document()
#    if request.headers['Content-Type'] == 'application/json':
#        for k in request.json.keys():
#            if doc_attribute_can_be_set(k):
#                settings[k] = request.json[k]
#        save_document(settings)
#        return Response(json.dumps(settings), status=200, mimetype='application/json')

    @patch('admin.views.get_group_document')
    def test_get_group_calls_get_group_document_when_group_found(self,
                                                                 av_get_group_document):
        av_get_group_document.return_value = {'v': 'm'}

        resp_object = av.get_group('123321')
        response_data_dict = json.loads(resp_object.data)

        av_get_group_document.assert_called_once_with('123321')
        assert resp_object.status_code == 200
        assert 'v' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('admin.views.get_group_document')
    def test_get_group_fails_when_group_not_found(self,
                                                  av_get_group_document):
        av_get_group_document.side_effect = NotFoundError('no group document found for 4422')
        resp_object = av.get_group('4422')
        av_get_group_document.assert_called_once_with('4422')
        assert resp_object.status_code == 404 
        assert resp_object.data == '"no group document found for 4422"'

    @patch('admin.views.find_pictures')
    @patch('admin.views.get_paging_info_from_request')
    @patch('admin.views.get_group_document')
    def test_get_group_pictures_calls_appropriate_methods(self,
                                                          av_get_group_document,
                                                          av_get_paging_info_from_request,
                                                          av_find_pictures):
        av_get_group_document.return_value = {'_id': '123'}
        av_get_paging_info_from_request.return_value = (2, 3)
        av_find_pictures.return_value = {'some_key': 'some_value'}

        resp_object = av.get_group_pictures('current')
        response_data_dict = json.loads(resp_object.data)

        av_get_group_document.assert_called_once_with('current')
        av_find_pictures.assert_called_once_with({'group_id': '123'}, page=2, items_per_page=3)
        assert resp_object.status_code == 200
        assert 'some_key' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('admin.views.find_pictures')
    @patch('admin.views.get_paging_info_from_request')
    @patch('admin.views.get_group_document')
    def test_get_group_pictures_handles_crash_in_find_pictures(self,
                                                               av_get_group_document,
                                                               av_get_paging_info_from_request,
                                                               av_find_pictures):
        av_get_group_document.return_value = {'_id': '123'}
        av_get_paging_info_from_request.return_value = (2, 'irish')
        av_find_pictures.side_effect = DocumentConfigurationError('invalid number specified for items_per_page: irish')

        resp_object = av.get_group_pictures('current')

        av_find_pictures.assert_called_once_with({'group_id': '123'}, page=2, items_per_page='irish')
        assert resp_object.status_code == 409 
        assert resp_object.data == '"invalid number specified for items_per_page: irish"'
