import os
from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import pytest

import picture.services as ps
import conftest
from thermal.exceptions import DocumentConfigurationError, NotFoundError
from thermal.utils import get_document, save_document


class TestPictureIntegration(object):

    def test_save_picture_document_works(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'picture'
        }
        ps.save_picture_document(picture_doc)
        new_picture_doc = get_document(the_pic_id)
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

    def test_build_picture_name_builds_picture_name_with_jpg(self):
        picture_id = uuid.uuid4()
        picture_name = ps.build_picture_name(picture_id)
        expected_name = str(picture_id) + '.jpg'
        assert expected_name == picture_name

    def test_build_picture_path_creates_directory_if_not_present(self):
        picture_name = 'whatever'
        snap_id = uuid.uuid4()
        assert not os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))
        picture_path = ps.build_picture_path(picture_name=picture_name, snap_id=snap_id)
        assert os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))

    def test_build_picture_path_does_not_create_directory_if_requested(self):
        picture_name = 'whatever'
        snap_id = uuid.uuid4()
        assert not os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))
        picture_path = ps.build_picture_path(picture_name=picture_name, snap_id=snap_id, create_directory=False)
        assert not os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))
