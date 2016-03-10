import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

from flask import current_app, request

import admin.views as av
from thermal.exceptions import DocumentConfigurationError, NotFoundError, ThermalBaseError


class TestViewsUnit(object):

    @patch('admin.views.generic_list_view')
    def test_list_groups_calls_generic_list_view(self,
                                                 av_generic_list_view):
        av_generic_list_view.return_value = {'6767': {'_id': '6767'},
                                             '7878': {'_id': '7878'}}

        resp_object = av.list_groups()

        av_generic_list_view.assert_called_once_with(document_type='group')

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

    @patch('admin.views.get_settings_document')
    def test_get_settings_catches_exceptions(self,
                                             av_get_settings_document):

        av_get_settings_document.side_effect = ThermalBaseError('blowing every time you move your teeth')

        resp_object = av.get_settings()
        assert resp_object.data == '"blowing every time you move your teeth"' 
        assert resp_object.status_code == 400

    @patch('admin.views.save_document')
    @patch('admin.views.get_settings_document')
    def test_update_settings_fails_when_bad_content_type(self,
                                                         av_get_settings_document,
                                                         av_save_document):
        av_get_settings_document.return_value = {'starfish': 'patrick'}
        with current_app.test_client() as c:
            resp_object = c.put('/api/v1/admin/settings',content_type='spongey')
            assert resp_object.data == '"no valid settings parameters supplied"'
            assert resp_object.status_code == 409


    @patch('admin.views.save_document')
    @patch('admin.views.doc_attribute_can_be_set')
    @patch('admin.views.get_settings_document')
    def test_update_settings_sets_allowed_values(self,
                                                 av_get_settings_document,
                                                 av_doc_attribute_can_be_set,
                                                 av_save_document):
        av_get_settings_document.return_value = {'starfish': 'patrick'}
        av_doc_attribute_can_be_set.return_value = True
        with current_app.test_client() as c:
            resp_object = c.put('/api/v1/admin/settings',
                                headers={'Content-Type':'application/json'},
                                data='{"ali":"g"}')
            assert resp_object.status_code == 200
            av_get_settings_document.assert_called_once_with()
            av_doc_attribute_can_be_set.assert_called_once_with('ali')
            av_save_document.assert_called_once_with({'starfish': 'patrick', 'ali': 'g'})

    @patch('admin.views.get_settings_document')
    def test_update_settings_catches_exceptions(self,
                                                av_get_settings_document):

        av_get_settings_document.side_effect = ThermalBaseError('Someones got it in for me, theyre planting stories in the press')

        resp_object = av.update_settings()
        assert resp_object.data == '"Someones got it in for me, theyre planting stories in the press"'
        assert resp_object.status_code == 400


    @patch('admin.views.save_document')
    @patch('admin.views.doc_attribute_can_be_set')
    @patch('admin.views.get_group_document')
    def test_update_group_sets_allowed_values(self,
                                              av_get_group_document,
                                              av_doc_attribute_can_be_set,
                                              av_save_document):
        av_get_group_document.return_value = {'eeny': 'meeny', 'teensy': 'weensy'}
        av_doc_attribute_can_be_set.return_value = True
        with current_app.test_client() as c:
            resp_object = c.put('/api/v1/admin/groups/876',
                                headers={'Content-Type':'application/json'},
                                data='{"eeny":"moe"}')
            assert resp_object.status_code == 200
            av_get_group_document.assert_called_once_with('876')
            av_doc_attribute_can_be_set.assert_called_once_with('eeny')
            av_save_document.assert_called_once_with({'eeny': 'moe', 'teensy': 'weensy'})


    @patch('admin.views.save_document')
    @patch('admin.views.get_group_document')
    def test_update_group_doesnt_set_disallowed_values(self,
                                                       av_get_group_document,
                                                       av_save_document):
        av_get_group_document.return_value = {'eeny': 'meeny', 'teensy': 'weensy'}
        with current_app.test_client() as c:
            resp_object = c.put('/api/v1/admin/groups/876',
                                headers={'Content-Type':'application/json'},
                                data='{"type":"unfortunate"}')
            assert resp_object.status_code == 200
            av_get_group_document.assert_called_once_with('876')
            av_save_document.assert_called_once_with({'eeny': 'meeny', 'teensy': 'weensy'})

    @patch('admin.views.get_group_document')
    def test_update_group_catches_exceptions(self,
                                             av_get_group_document):

        av_get_group_document.side_effect = ThermalBaseError('Blowing through the curtains in your room')

        resp_object = av.update_group('brockman')
        assert resp_object.data == '"Blowing through the curtains in your room"'
        assert resp_object.status_code == 400

    @patch('admin.views.get_settings_document')
    def test_save_group_catches_exceptions(self,
                                           av_get_settings_document):

        av_get_settings_document.side_effect = ThermalBaseError('You tamed the lion in my cage')

        resp_object = av.save_group()
        assert resp_object.data == '"You tamed the lion in my cage"'
        assert resp_object.status_code == 400


    @patch('admin.views.get_group_document_with_child_objects')
    @patch('admin.views.get_group_document_with_child_links')
    @patch('admin.views.get_group_document')
    def test_get_group_calls_get_group_document_when_group_found(self,
                                                                 av_get_group_document,
                                                                 av_get_group_document_with_child_links,
                                                                 av_get_group_document_with_child_objects):
        av_get_group_document.return_value = {'v': 'm'}
        resp_object = current_app.test_client().get('/api/v1/admin/groups/123321')
        response_data_dict = json.loads(resp_object.data)

        av_get_group_document.assert_called_once_with('123321')
        av_get_group_document_with_child_links.assert_not_called()
        av_get_group_document_with_child_objects.assert_not_called()
        assert resp_object.status_code == 200
        assert 'v' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('admin.views.get_group_document_with_child_objects')
    @patch('admin.views.get_group_document_with_child_links')
    @patch('admin.views.get_group_document')
    def test_get_group_fails_when_group_not_found(self,
                                                  av_get_group_document,
                                                  av_get_group_document_with_child_links,
                                                  av_get_group_document_with_child_objects):
        av_get_group_document.side_effect = NotFoundError('no group document found for 4422')
        resp_object = current_app.test_client().get('/api/v1/admin/groups/4422')
        av_get_group_document.assert_called_once_with('4422')
        assert resp_object.status_code == 404
        assert resp_object.data == '"no group document found for 4422"'


    @patch('admin.views.get_group_document_with_child_objects')
    @patch('admin.views.get_group_document_with_child_links')
    @patch('admin.views.get_group_document')
    def test_get_group_gets_child_links_when_requested(self,
                                                       av_get_group_document,
                                                       av_get_group_document_with_child_links,
                                                       av_get_group_document_with_child_objects):
        av_get_group_document_with_child_links.return_value = {'r': 'q'}
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/admin/groups/123321?child_links=x')
            av_get_group_document.assert_not_called()
            av_get_group_document_with_child_links.assert_called_once_with('123321')
            av_get_group_document_with_child_objects.assert_not_called()
            response_data_dict = json.loads(resp_object.data)
            assert request.args['child_links'] == 'x'
            assert resp_object.status_code == 200
            assert 'r' in response_data_dict
            assert len(response_data_dict.keys()) == 1


    @patch('admin.views.get_group_document_with_child_objects')
    @patch('admin.views.get_group_document_with_child_links')
    @patch('admin.views.get_group_document')
    def test_get_group_gets_child_objects_when_requested(self,
                                                         av_get_group_document,
                                                         av_get_group_document_with_child_links,
                                                         av_get_group_document_with_child_objects):
        av_get_group_document_with_child_objects.return_value = {'m': 's'}
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/admin/groups/123321?child_objects=x')
            av_get_group_document.assert_not_called()
            av_get_group_document_with_child_links.assert_not_called()
            av_get_group_document_with_child_objects.assert_called_once_with('123321')
            response_data_dict = json.loads(resp_object.data)
            assert request.args['child_objects'] == 'x'
            assert resp_object.status_code == 200
            assert 'm' in response_data_dict
            assert len(response_data_dict.keys()) == 1


    @patch('admin.views.get_group_document_with_child_objects')
    @patch('admin.views.get_group_document_with_child_links')
    @patch('admin.views.get_group_document')
    def test_get_group_gets_child_objects_when_both_links_and_objects_are_requested(self,
                                                                                    av_get_group_document,
                                                                                    av_get_group_document_with_child_links,
                                                                                    av_get_group_document_with_child_objects):
        av_get_group_document_with_child_objects.return_value = {'o': 'i'}
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/admin/groups/123321?child_objects=x&child_links=y')
            av_get_group_document.assert_not_called()
            av_get_group_document_with_child_links.assert_not_called()
            av_get_group_document_with_child_objects.assert_called_once_with('123321')
            response_data_dict = json.loads(resp_object.data)
            assert request.args['child_objects'] == 'x'
            assert request.args['child_links'] == 'y'
            assert resp_object.status_code == 200
            assert 'o' in response_data_dict
            assert len(response_data_dict.keys()) == 1


    @patch('admin.views.search_generic')
    @patch('admin.views.get_group_document')
    def test_get_group_pictures_calls_appropriate_methods(self,
                                                          av_get_group_document,
                                                          av_search_generic):
        av_get_group_document.return_value = {'_id': '123'}
        av_search_generic.return_value = {'some_key': 'some_value'}

        resp_object = av.get_group_pictures('current')
        response_data_dict = json.loads(resp_object.data)

        av_get_group_document.assert_called_once_with('current')
        av_search_generic.assert_called_once_with(document_type='picture', 
                                                  args_dict={'group_id': '123'})
        assert resp_object.status_code == 200
        assert 'some_key' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('admin.views.get_group_document')
    def test_get_group_pictures_catches_exceptions(self,
                                                   av_get_group_document):

        av_get_group_document.side_effect = ThermalBaseError('flies buzzing around your eyes')

        resp_object = av.get_group_pictures('yyz')
        assert resp_object.data == '"flies buzzing around your eyes"'
        assert resp_object.status_code == 400

    @patch('admin.views.search_generic')
    @patch('admin.views.get_group_document')
    def test_get_group_gallery_calls_appropriate_methods(self,
                                                         av_get_group_document,
                                                         av_search_generic):
        av_get_group_document.return_value = {'_id': '123'}
        av_search_generic.return_value = {'some_key': 'some_value'}

        resp_object = av.get_group_gallery('current')
        response_data_dict = json.loads(resp_object.data)

        av_get_group_document.assert_called_once_with('current')
        av_search_generic.assert_called_once_with(document_type='picture',
                                                  args_dict={'group_id': '123',
                                                             'gallery_url_not_null': True})
        assert resp_object.status_code == 200
        assert 'some_key' in response_data_dict
        assert len(response_data_dict.keys()) == 1

    @patch('admin.views.get_group_document')
    def test_get_group_gallery_catches_exceptions(self,
                                                  av_get_group_document):

        av_get_group_document.side_effect = ThermalBaseError('beware of lightning that might strike')

        resp_object = av.get_group_gallery('barchetta')
        assert resp_object.data == '"beware of lightning that might strike"'
        assert resp_object.status_code == 400

    @patch('admin.views.save_document')
    @patch('admin.views.doc_attribute_can_be_set')
    @patch('admin.views.get_settings_document')
    def test_add_group_adds_a_group(self,
                                    av_get_settings_document,
                                    av_doc_attribute_can_be_set,
                                    av_save_document):
        av_get_settings_document.return_value = {'bread': 'pudding'}
        
        av_doc_attribute_can_be_set.return_value = True
        with current_app.test_client() as c:
            resp_object = c.post('/api/v1/admin/groups',
                                 data='{"dog":"food"}',
                                 headers={'Content-Type':'application/json'})
            assert resp_object.status_code == 200

            resp_data_dict = json.loads(resp_object.data)
            group_id = resp_data_dict['_id']
            group_dict_for_call = av.default_group_dict()
            group_dict_for_call['dog'] = 'food'
            group_dict_for_call['_id'] = group_id

            av_get_settings_document.assert_called_once_with()
            av_doc_attribute_can_be_set.assert_called_once_with('dog')

            group_save_call = call(group_dict_for_call)
            settings_save_call = call({'bread': 'pudding', 'current_group_id': group_id})
            av_save_document.assert_has_calls([group_save_call, settings_save_call])

    @patch('admin.views.get_url_base')
    def test_index_shows_links(self, av_get_url_base):
        av_get_url_base.return_value = 'prawn'
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/admin/')

            response_data_dict = json.loads(resp_object.data)

            assert resp_object.status_code == 200
            assert 'settings' in response_data_dict
            assert 'prawn' in response_data_dict['settings']
            assert 'groups' in response_data_dict
            assert 'prawn' in response_data_dict['groups']
            assert len(response_data_dict.keys()) == 2
            av_get_url_base.assert_called_once_with()


class TestViewsIntegration(object):
    pass
# TODO this will need an integration test because that gallery_url_not_null is a little special
# @admin.route('/groups/<group_id>/gallery', methods=['GET'])
