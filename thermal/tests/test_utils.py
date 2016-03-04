import os
from mock import ANY, call, Mock, patch
import uuid

import boto
from flask import current_app
import pytest

import conftest
from thermal.exceptions import DocumentConfigurationError
import thermal.utils as tu


class TestUtilsUnit(object):

    def test_get_paging_info_returns_ok_with_good_paging_info(self):
        kwargs = {'page': '1', 'items_per_page': '2'}

        (paging_requested, start_index, end_index) = tu.get_paging_info(**kwargs)
        assert paging_requested
        assert start_index == 0
        assert end_index == 1

    def test_get_paging_info_fails_with_nonnumeric_page_number(self):
        kwargs = {'page': 'x', 'items_per_page': '2'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            (paging_requested, start_index, end_index) = tu.get_paging_info(**kwargs)
        assert 'invalid number specified for page' in str(exception_info.value)

    def test_get_paging_info_fails_with_negative_page_number(self):
        kwargs = {'page': '-1', 'items_per_page': '2'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            (paging_requested, start_index, end_index) = tu.get_paging_info(**kwargs)
        assert 'page number must be a number greater than zero' in str(exception_info.value)

    def test_get_paging_info_fails_with_nonnumeric_items_per_page(self):
        kwargs = {'page': '1', 'items_per_page': 'x'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            (paging_requested, start_index, end_index) = tu.get_paging_info(**kwargs)
        assert 'invalid number specified for items_per_page' in str(exception_info.value)

    def test_get_paging_info_fails_with_negative_items_per_page(self):
        kwargs = {'page': '1', 'items_per_page': '-2'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            (paging_requested, start_index, end_index) = tu.get_paging_info(**kwargs)
        assert 'items_per_page must be a number greater than zero' in str(exception_info.value)

    def test_doc_attribute_can_be_set_works_for_normal_and_forbidden_keys(self):
        assert tu.doc_attribute_can_be_set('lester')
        assert not tu.doc_attribute_can_be_set('_id')
        assert not tu.doc_attribute_can_be_set('_rev')

    def test_save_document_fails_if_document_type_is_being_altered(self):
        the_id = str(uuid.uuid4())
        the_doc = {'_id': the_id, 'type': 'something'}
        current_app.db[the_id] = the_doc
        the_doc['type'] = 'something else'
        with pytest.raises(DocumentConfigurationError):
            tu.save_document(the_doc)

    def test_get_parameter_fetches_parameter_when_all_is_well(self):
        with current_app.test_request_context('/whatever?the_parameter=the_value'):
            from flask import request  # I know, crazy, but you need to import request here, not at the top of the module
            assert 'the_parameter' in request.args
            fetched_value = tu.get_parameter('the_parameter')
            assert fetched_value == 'the_value'

    def test_get_parameter_fetches_None_when_no_parameter_and_no_default(self):
        with current_app.test_request_context('/whatever?the_parameter=the_value'):
            fetched_value = tu.get_parameter('mike_ptyson')
            assert fetched_value == None

    def test_get_parameter_fetches_default_when_no_parameter_and_default_specified(self):
        with current_app.test_request_context('/whatever?the_parameter=the_value'):
            fetched_value = tu.get_parameter('mike_ptyson', default='john_abercrombie')
            assert fetched_value == 'john_abercrombie'

    def test_get_parameter_returns_string_by_default(self):
        with current_app.test_request_context('/whatever?the_parameter=66'):
            fetched_value = tu.get_parameter('the_parameter')
            assert type(fetched_value).__name__ == 'unicode'
            assert fetched_value == '66'

    def test_get_parameter_can_cast_a_value_to_int(self):
        with current_app.test_request_context('/whatever?the_parameter=66'):
            fetched_value = tu.get_parameter('the_parameter', cast_to_type=int)
            assert type(fetched_value).__name__ == 'int'
            assert fetched_value == 66

    def test_get_parameter_returns_none_when_cast_fails_and_no_default_and_no_raise_value_error(self):
        with current_app.test_request_context('/whatever?the_parameter=baloney'):
            fetched_value = tu.get_parameter('the_parameter', cast_to_type=int)
            assert fetched_value == None

    def test_get_parameter_returns_default_when_cast_fails_and_default_specified_and_no_raise_value_error(self):
        with current_app.test_request_context('/whatever?the_parameter=baloney'):
            fetched_value = tu.get_parameter('the_parameter', default='monkey_chow', cast_to_type=int)
            assert fetched_value == 'monkey_chow'

    def test_get_parameter_raises_valueerror_when_cast_fails_and_default_specified_and_raise_value_error_requested(self):
        with current_app.test_request_context('/whatever?the_parameter=baloney'):
            with pytest.raises(ValueError) as exception_info:
                fetched_value = tu.get_parameter('the_parameter', default='monkey_chow', cast_to_type=int, raise_value_error=True)
            assert 'problem casting parameter the_parameter (value baloney) as type int' in str(exception_info.value)
## TODO test all the branches of this
#def get_parameter(parameter_name, default=None, cast_to_type=None, raise_value_error=False):
#    '''
#    Fetches a value from the request args
#    You can specify a default value.  If you do not it uses None
#    You can specify a default data type.  If you do not it uses string
#    If no parameter for that name is found it returns the default
#    If you specify a cast_to_type it will attempt to cast the string to that type.  
#      - If the cast fails and you don't specify raise_value_error it returns the default value
#      - If the cast fails and you do specify raise_value_error it raises a ValueError with info in its detail message
#    '''
#    return_value = default
#    if parameter_name in request.args:
#        return_value = request.args.get(parameter_name)
#        if cast_to_type:
#            try:
#                return_value = cast_to_type(return_value)
#            except ValueError as e:
#                if raise_value_error:
#                    error_string = "problem casting parameter {0} (value {1} as type {2}".format(str(paramater_name),
#                                                                                                 str(return_value),
#                                                                                                 str(cast_to_type.__name__))
#                    raise ValueError(error_string)
#                else:
#                    return_value = default
#    return return_value







class TestUtilsIntegration(object):

    def test_get_documents_from_criteria_fetches_by_arbitrary_criterion(self):
        id_1 = str(uuid.uuid4())
        the_doc = {'doctor': 'strangelove'}
        current_app.db[id_1] = the_doc
        id_2 = str(uuid.uuid4())
        the_doc = {'doctor': 'demento'}
        current_app.db[id_2] = the_doc
        id_3 = str(uuid.uuid4())
        the_doc = {'doctor': 'detroit'}
        current_app.db[id_3] = the_doc
        args_dict = {'doctor': 'demento'}

        documents = tu.get_documents_from_criteria(args_dict)

        assert len(documents.keys()) == 1
        assert id_2 in documents

    def test_get_documents_from_criteria_recognizes_gallery_url_not_noll_kwarg(self):
        id_1 = str(uuid.uuid4())
        the_doc = {'doctor': 'strangelove', 'gallery_url': 'something'}
        current_app.db[id_1] = the_doc
        id_2 = str(uuid.uuid4())
        the_doc = {'doctor': 'strangelove'}
        current_app.db[id_2] = the_doc

        args_dict = {'doctor': 'strangelove'}

        documents = tu.get_documents_from_criteria(args_dict, gallery_url_not_null=True)

        assert len(documents.keys()) == 1
        assert id_1 in documents

    def test_item_exists_returns_true_when_item_exists(self):
        item_id = uuid.uuid4()
        doc_1 = {
            '_id': str(item_id),
            'type': 'picture'
        }
        tu.save_document(doc_1)

        assert tu.item_exists(item_id, 'picture')

    def test_item_exists_returns_false_when_item_does_not_exist(self):
        item_id = uuid.uuid4()

        assert not tu.item_exists(item_id, 'anything')
