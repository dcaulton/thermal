from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest 

import camera.tasks as ct
from camera.services import take_picam_still

class TestTasksUnit(object):

    @patch('camera.services.take_picam_still')
    def test_picam_still_calls_camera_services(self, cs_take_picam_still):
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        ct.take_picam_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=0)
        cs_take_picam_still.assert_called_once_with(snap_id, group_id, ANY, ANY)

    @patch('camera.services.take_picam_still')
    def test_picam_still_calls_camera_services_multiple_times_when_repeat_specified(self, cs_take_picam_still):
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        ct.take_picam_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=2)
        call_1 = call(snap_id, group_id, ANY, ANY)
        call_2 = call(ANY, group_id, ANY, ANY)
        call_3 = call(ANY, group_id, ANY, ANY)
        calls = [call_1, call_2, call_3]
        cs_take_picam_still.assert_has_calls(calls)
