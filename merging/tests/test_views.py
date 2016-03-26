import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

from flask import current_app, request

import merging.views as mv
import merging.services
from thermal.exceptions import DocumentConfigurationError, NotFoundError, ThermalBaseError


class TestViewsUnit(object):

    @patch('merging.views.get_url_base')
    def test_index_shows_links(self, mv_get_url_base):
        mv_get_url_base.return_value = 'flounder'
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/merging/')

            response_data_dict = json.loads(resp_object.data)

            assert resp_object.status_code == 200
            assert 'merge_images' in response_data_dict
            assert 'flounder' in response_data_dict['merge_images']
            assert len(response_data_dict.keys()) == 1
            mv_get_url_base.assert_called_once_with()


    @patch('merging.views.item_exists')
    def test_test_input_parameters_for_valid_image_ids_checks_for_both_images(self,
                                                                              mv_item_exists):
        mv_item_exists.return_value = True
        mv.test_input_parameters_for_valid_image_ids({'img1_id': 'johnny', 'img2_id': 'depp'})
        mv_item_exists.assert_has_calls([call('johnny', 'picture'), call('depp', 'picture')])

    @patch('merging.views.item_exists')
    def test_test_input_parameters_for_valid_image_ids_raises_notfounderror(self,
                                                                            mv_item_exists):
        mv_item_exists.return_value = False
        with pytest.raises(NotFoundError) as exception_info:
            mv.test_input_parameters_for_valid_image_ids({'img1_id': 'johnny', 'img2_id': 'depp'})
        mv_item_exists.assert_called_once_with('johnny', 'picture')
        assert 'Source image 1 not found.  A valid id for a source image must be supplied' in str(exception_info.value)

    @patch('merging.views.merge_type_is_valid')
    def test_check_for_merge_type_raises_documentconfigurationerror(self,
                                                                    mv_merge_type_is_valid):
        mv_merge_type_is_valid.return_value = False

        with pytest.raises(DocumentConfigurationError) as exception_info:
            mv.check_for_merge_type({'merge_type': 'bamboozle'})
        mv_merge_type_is_valid.assert_called_once_with('bamboozle')
        assert 'invalid merge type specified: bamboozle' in str(exception_info.value)

    @patch('merging.views.merge_type_is_valid')
    def test_check_for_merge_type_fetches_valid_merge_type(self,
                                                           mv_merge_type_is_valid):
        mv_merge_type_is_valid.return_value = True
        return_value = mv.check_for_merge_type({'merge_type': 'bamboozle'})
        assert return_value == 'bamboozle'

    def test_check_for_merge_type_returns_nothing_when_no_type_supplied(self):
        return_value = mv.check_for_merge_type({})
        assert return_value == None


    @patch('merging.views.gather_and_enforce_request_args')
    @patch('merging.views.test_input_parameters_for_valid_image_ids')
    @patch('merging.views.check_for_merge_type')
    @patch('merging.views.cast_uuid_to_string')
    def test_call_merge_images_calls_expected_methods(self,
                                                      mv_cast_uuid_to_string,
                                                      mv_check_for_merge_type,
                                                      mv_test_input_parameters_for_valid_image_ids,
                                                      mv_gather_and_enforce_request_args):
        the_args_dict = {'img1_id': 'professor', 'img2_id': 'mary_ann'}
        mv_gather_and_enforce_request_args.return_value = the_args_dict
        mv_check_for_merge_type.return_value = 'gilligan'
        mv_cast_uuid_to_string.return_value = 'skipper'

        merging.services.merge_images = Mock()
        resp_object = mv.call_merge_images()

        mv_gather_and_enforce_request_args.assert_called_once_with([{'name': 'img1_id', 'required': True},
                                                                    {'name': 'img2_id', 'required': True},
                                                                    {'name': 'merge_type'}])
        mv_test_input_parameters_for_valid_image_ids.assert_called_once_with(the_args_dict)
        mv_check_for_merge_type.assert_called_once_with(the_args_dict)
        mv_cast_uuid_to_string.assert_called_once_with(ANY)
        merging.services.merge_images.assert_called_once_with(img1_primary_id_in='professor',
                                                              img1_alternate_id_in=ANY,
                                                              img2_id_in='mary_ann',
                                                              img_id_out='skipper',
                                                              group_id='current',
                                                              merge_type='gilligan')
        assert resp_object.status_code == 202


    @patch('merging.views.gather_and_enforce_request_args')
    def test_call_merge_images_handles_exception(self,
                                                 mv_gather_and_enforce_request_args):

        mv_gather_and_enforce_request_args.side_effect = ThermalBaseError('careless_whisper')

        resp_object = mv.call_merge_images()
        assert resp_object.data == '"careless_whisper"'
        assert resp_object.status_code == 400
