import json
from mock import ANY, call, Mock, patch
import uuid

import admin.views as av


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

