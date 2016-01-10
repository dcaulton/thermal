from mock import ANY, Mock, patch
import uuid

from flask import current_app
import mock
import pytest 

from camera.cameras import Lepton
import camera.services as cs


class TestServicesUnit(object):

    @patch('camera.services.save_picture')
    def test_thermal_still_saves_appropriate_picture_document(self, cs_save_picture):

        Lepton.take_still = Mock()
        #here's how to set properties on the function we mocked out
        #  cs_save_picture.return_value = 'haha'
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        pic_id = uuid.uuid4()

        cs.take_thermal_still(snap_id, group_id, pic_id)

        picture_name = cs.build_picture_name(pic_id)
        picture_path = cs.build_pic_path(picture_name)

        cs.save_picture.assert_called_once_with(
            {'_id': str(pic_id),
             'type': 'picture',
             'source': 'thermal',
             'group_id': str(group_id),
             'snap_id': str(snap_id),
             'filename': picture_name,
             'uri': ANY,
             'created': ANY
            }
        )

    def test_thermal_still_calls_lepton_camera_class(self):
        Lepton.take_still = Mock()
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        pic_id = uuid.uuid4()

        cs.take_thermal_still(snap_id, group_id, pic_id)

        pic_doc = current_app.db[str(pic_id)]
        picture_name = cs.build_picture_name(pic_id)
        picture_path = cs.build_pic_path(picture_name)
        Lepton.take_still.assert_called_once_with(pic_path=picture_path)
        #the above works because we re-declared take_still as a mock for this method
        #  coming into this method it's already a mock because it was declared a mock earlier
        #  in the class.  In this case it's okay, we're never gonna want to call the hardware for 
        #  unit tests but the same behavior isn't wanted from other methods, that's where patch comes in
