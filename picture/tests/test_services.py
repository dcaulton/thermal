import os
import uuid

from flask import current_app
import pytest

import picture.services as ps
import conftest


class TestPictureIntegration(object):

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
