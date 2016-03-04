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
