import os
from mock import ANY, call, Mock, patch
import uuid

import boto
from flask import current_app
import pytest 

import conftest
import thermal.utils

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
