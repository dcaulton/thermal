import os
import uuid

from flask import current_app
from mock import ANY, call, Mock, patch
import pytest

from thermal.exceptions import DocumentConfigurationError, NotFoundError
import thermal.services as ts
import conftest


class TestServiceUnit(object):

    @patch('thermal.services.gather_and_enforce_request_args')   
    @patch('thermal.services.get_documents_from_criteria')
    def test_search_generic_calls_expected_functions(self,
                                                     ts_get_documents_from_criteria,
                                                     ts_gather_and_enforce_request_args):
        ts_gather_and_enforce_request_args.return_value = {'coco': 'puffs'}
        ts_get_documents_from_criteria.return_value = {'franken': 'berry'}

        ret_val = ts.search_generic(document_type='cereal', args_dict={'special': 'k'})

        assert ts_gather_and_enforce_request_args.called_once_with(['ANY_SEARCHABLE'])
        assert ts_get_documents_from_criteria.called_once_with({'special': 'k',
                                                                'coco': 'puffs',
                                                                'type': 'cereal'})
        assert ret_val == {'franken': 'berry'}

    @patch('thermal.services.item_exists')   
    @patch('thermal.services.get_document')
    def test_get_generic_calls_expected_functions(self,
                                                  ts_get_document,
                                                  ts_item_exists):
        ts_item_exists.return_value = True
        ts_get_document.return_value = {'gabe': 'kaplan'}

        item_id = uuid.uuid4()
        ret_val = ts.get_generic(item_id, 'teacher')

        assert ts_item_exists.called_once_with(item_id, 'teacher')
        assert ts_get_document.called_once_with(item_id)
        assert ret_val == {'gabe': 'kaplan'}

    @patch('thermal.services.item_exists')   
    @patch('thermal.services.get_document')
    def test_get_generic_throws_error_when_item_doesnt_exist(self,
                                                             ts_get_document,
                                                             ts_item_exists):
        ts_item_exists.return_value = False

        item_id = uuid.uuid4()
        with pytest.raises(NotFoundError) as exception_info:
            ret_val = ts.get_generic(item_id, 'teacher')
        assert 'teacher not found for id {0}'.format(str(item_id))  in str(exception_info.value)


    @patch('thermal.services.save_document')   
    def test_save_generic_calls_expected_functions(self,
                                                   ts_save_document):
        ret_val = ts.save_generic({'a': 'b'})
        assert ts_save_document.called_once_with({'a': 'b'})

    @patch('thermal.services.cast_uuid_to_string')   
    @patch('thermal.services.item_exists')
    @patch('thermal.services.save_document')
    def test_update_generic_calls_expected_functions(self,
                                                     ts_save_document,
                                                     ts_item_exists,
                                                     ts_cast_uuid_to_string):
        ts_item_exists.return_value = True
        ts_cast_uuid_to_string.return_value = 'abc'

        item_id = uuid.uuid4()
        the_document = {'_id': item_id}

        ret_val = ts.update_generic(the_document, 'plastic')

        ts_cast_uuid_to_string.assert_called_once_with(item_id)
        ts_item_exists.assert_has_calls([call('abc', 'any'), call('abc', 'plastic')])
        ts_save_document.assert_called_once_with(the_document)

    def test_update_generic_throws_error_when_no_doc_id(self):
        the_document = {'insect': 'beetle'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            ret_val = ts.update_generic(the_document, 'color')
        assert 'trying to update a document with no id' in str(exception_info.value)

    @patch('thermal.services.item_exists')
    def test_update_generic_throws_error_when_no_doc_exists(self,
                                                            ts_item_exists):
        ts_item_exists.return_value = False

        item_id = uuid.uuid4()
        the_document = {'_id': item_id}

        with pytest.raises(DocumentConfigurationError) as exception_info:
            ret_val = ts.update_generic(the_document, 'whatever')
        assert 'trying to update {0} when no document exists for that id'.format(str(item_id)) in str(exception_info.value)

class TestServiceIntegration(object):

    def test_update_generic_throws_error_when_no_doc_of_the_right_type_exists_and_is_specified_in_call(self):
        the_id = str(uuid.uuid4())
        the_document = {'_id': the_id, 'type': 'ringo'}
        current_app.db[the_id] = the_document

        with pytest.raises(DocumentConfigurationError) as exception_info:
            ret_val = ts.update_generic(the_document, 'paul')
        assert 'trying to alter document type for id {0} during update'.format(str(the_id)) in str(exception_info.value)
