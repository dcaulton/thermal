import json
from mock import ANY, call, Mock, patch
import uuid

from flask import current_app, request

import analysis.views as av
from thermal.exceptions import ThermalBaseError


class TestViewsUnit(object):

    @patch('analysis.views.get_url_base')
    def test_index_shows_links(self, av_get_url_base):
        av_get_url_base.return_value = 'grouper'
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/analysis/')

            response_data_dict = json.loads(resp_object.data)

            assert resp_object.status_code == 200
            assert 'scale_image' in response_data_dict
            assert 'grouper' in response_data_dict['scale_image']
            assert 'edge_detect' in response_data_dict
            assert 'grouper' in response_data_dict['edge_detect']
            assert len(response_data_dict.keys()) == 2
            av_get_url_base.assert_called_once_with()


    @patch('analysis.views.item_exists')
    @patch('analysis.services.scale_image_task.delay')
    def test_scale_image_calls_appropriate_methods_when_image_exists(self,
                                                                     av_scale_image_task_delay,
                                                                     av_item_exists):
        av_item_exists.return_value = True

        resp_object = av.call_scale_image(image_id='4242')

        av_item_exists.assert_called_once_with('4242', 'picture')
        av_scale_image_task_delay.assert_called_once_with(img_id_in='4242', img_id_out=ANY, group_id='current')

        response_data_dict = json.loads(resp_object.data)
        assert resp_object.status_code == 202
        assert response_data_dict == {'scale_image_output_image_id': ANY}


    @patch('analysis.views.item_exists')
    def test_scale_image_handles_image_not_existing(self,
                                                    av_item_exists):
        av_item_exists.return_value = False

        resp_object = av.call_scale_image(image_id='4242')

        av_item_exists.assert_called_once_with('4242', 'picture')
        assert resp_object.status_code == 404


    @patch('analysis.views.get_document_with_exception')
    @patch('analysis.views.gather_and_enforce_request_args')
    @patch('analysis.services.edge_detect_task.delay')
    def test_call_edge_detect_calls_appropriate_methods_for_defaults(self,
                                                                     av_edge_detect_task_delay,
                                                                     av_gather_and_enforce_request_args,
                                                                     av_get_document_with_exception):
        av_get_document_with_exception.return_value = {'hamburger': 'man'}
        av_gather_and_enforce_request_args.return_value = {'detection_threshold': 'all'}

        resp_object = av.call_edge_detect(image_id='5454')

        av_get_document_with_exception.assert_called_once_with('5454', document_type='picture')
        av_gather_and_enforce_request_args.assert_called_once_with([{'name': 'detection_threshold', 'default': 'all'}])

        av_edge_detect_task_delay.assert_called_once_with(img_id_in='5454',
                                                          detection_threshold='all',
                                                          auto_id=ANY,
                                                          wide_id=ANY,
                                                          tight_id=ANY)
        response_data_dict = json.loads(resp_object.data)
        assert 'auto_id' in response_data_dict
        assert 'wide_id' in response_data_dict
        assert 'tight_id' in response_data_dict
        assert len(response_data_dict.keys()) == 3

        assert resp_object.status_code == 202


    @patch('analysis.views.get_document_with_exception')
    @patch('analysis.views.gather_and_enforce_request_args')
    def test_call_edge_detect_handles_bad_detection_threshold(self,
                                                              av_gather_and_enforce_request_args,
                                                              av_get_document_with_exception):
        av_get_document_with_exception.return_value = {'hamburger': 'man'}
        av_gather_and_enforce_request_args.return_value = {'detection_threshold': 'monkey_chow'}

        resp_object = av.call_edge_detect(image_id='5454')

        av_get_document_with_exception.assert_called_once_with('5454', document_type='picture')
        av_gather_and_enforce_request_args.assert_called_once_with([{'name': 'detection_threshold', 'default': 'all'}])
        assert resp_object.data == '"invalid detection threshold specified.  Allowable are all, auto, wide or tight"'
        assert resp_object.status_code == 409

    @patch('analysis.views.get_document_with_exception')
    def test_call_edge_detect_handles_exceptions(self,
                                                 av_get_document_with_exception):
        av_get_document_with_exception.side_effect = ThermalBaseError('dale gribble')

        resp_object = av.call_edge_detect(image_id='5454')

        av_get_document_with_exception.assert_called_once_with('5454', document_type='picture')
        assert resp_object.data == '"dale gribble"'
        assert resp_object.status_code == 400
