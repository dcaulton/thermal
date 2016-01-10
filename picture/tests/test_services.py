from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import pytest 

import picture.services as ps
import conftest
from thermal.exceptions import DocumentConfigurationError, NotFoundError


class TestPictureUnit(object):
    def test_find_picture_finds_the_correct_picture_document(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'picture'
        }
        current_app.db[the_pic_id] = picture_doc
        new_picture_doc = ps.find_picture(the_pic_id)
        assert new_picture_doc['_id'] == the_pic_id
        assert new_picture_doc['type'] == 'picture'
        assert '_rev' in new_picture_doc

    def test_find_picture_fails_if_the_picture_doesnt_exist(self):
        the_id = str(uuid.uuid4())
        with pytest.raises(NotFoundError):
            the_returned_doc = ps.find_picture(the_id)

    def test_save_picture_document_works(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'picture'
        }
        ps.save_picture_document(picture_doc)
        new_picture_doc = ps.find_picture(the_pic_id)
        assert new_picture_doc['_id'] == the_pic_id

    def test_save_picture_document_fails_if_picture_already_in_db(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'picture'
        }
        ps.save_picture_document(picture_doc)
        with pytest.raises(DocumentConfigurationError):
            ps.save_picture_document(picture_doc)

    def test_save_picture_document_fails_if_no_type_defined(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id
        }
        with pytest.raises(DocumentConfigurationError):
            ps.save_picture_document(picture_doc)

    def test_save_picture_document_fails_if_type_is_not_picture(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'not_picture'
        }
        with pytest.raises(DocumentConfigurationError):
            ps.save_picture_document(picture_doc)
