import uuid

from flask import current_app
import mock
import pytest 

import conftest
from camera.cameras import Lepton
from camera.services import build_pic_path, build_picture_name, take_thermal_still


class TestServicesUnit(object):
    def test_thermal_still_saves_appropriate_picture_document(self):
        Lepton.take_still = mock.Mock()
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        pic_id = uuid.uuid4()

        take_thermal_still(snap_id, group_id, pic_id)

        # TODO fetching the doc from the db means this is actually integration testing.
        #  put a wrapper around the picture save in the service, then check what it was called with.
        #  integration tests are still good, just don't put it here, in the unit test section
        pic_doc = current_app.db[str(pic_id)]
        picture_name = build_picture_name(pic_id)
        picture_path = build_pic_path(picture_name)
        assert '_id' in pic_doc.keys()
        assert '_rev' in pic_doc.keys()
        assert 'created' in pic_doc.keys()
        assert pic_doc['type'] == 'picture'
        assert pic_doc['source'] == 'thermal'
        assert pic_doc['group_id'] == str(group_id)
        assert pic_doc['snap_id'] == str(snap_id)
        assert str(pic_id) in pic_doc['filename']
        assert str(pic_id) in pic_doc['uri']

    def test_thermal_still_calls_lepton_camera_class(self):
        Lepton.take_still = mock.Mock()
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        pic_id = uuid.uuid4()

        take_thermal_still(snap_id, group_id, pic_id)

        pic_doc = current_app.db[str(pic_id)]
        picture_name = build_picture_name(pic_id)
        picture_path = build_pic_path(picture_name)
        Lepton.take_still.assert_called_once_with(pic_path=picture_path)
