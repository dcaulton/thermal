import os
from mock import ANY, call, Mock, patch
import uuid

import boto
from flask import current_app
import pytest 

import conftest
from thermal.exceptions import DocumentConfigurationError
import thermal.utils

class TestUtilsUnit(object):
    def test_get_paging_info_returns_ok_with_good_paging_info(self):
        kwargs = {'page': '1', 'items_per_page': '2'}

        (paging_requested, start_index, end_index) = thermal.utils.get_paging_info(**kwargs)
        assert paging_requested == True
        assert start_index == 0
        assert end_index == 1

    def test_get_paging_info_fails_with_nonnumeric_page_number(self):
        kwargs = {'page': 'x', 'items_per_page': '2'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            (paging_requested, start_index, end_index) = thermal.utils.get_paging_info(**kwargs)
        assert 'invalid number specified for page' in str(exception_info.value)


    def test_get_paging_info_fails_with_negative_page_number(self):
        kwargs = {'page': '-1', 'items_per_page': '2'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            (paging_requested, start_index, end_index) = thermal.utils.get_paging_info(**kwargs)
        assert 'page number must be a number greater than zero' in str(exception_info.value)

    def test_get_paging_info_fails_with_nonnumeric_items_per_page(self):
        kwargs = {'page': '1', 'items_per_page': 'x'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            (paging_requested, start_index, end_index) = thermal.utils.get_paging_info(**kwargs)
        assert 'invalid number specified for items_per_page' in str(exception_info.value)

    def test_get_paging_info_fails_with_negative_items_per_page(self):
        kwargs = {'page': '1', 'items_per_page': '-2'}
        with pytest.raises(DocumentConfigurationError) as exception_info:
            (paging_requested, start_index, end_index) = thermal.utils.get_paging_info(**kwargs)
        assert 'items_per_page must be a number greater than zero' in str(exception_info.value)


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

        documents = thermal.utils.get_documents_from_criteria(args_dict)

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

        documents = thermal.utils.get_documents_from_criteria(args_dict, gallery_url_not_null=True)

        assert len(documents.keys()) == 1
        assert id_1 in documents
