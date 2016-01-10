from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest 

from camera.cameras import Lepton, Picam
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

    @patch('camera.services.save_picture')
    def test_picam_still_saves_appropriate_normal_exposure_picture_document(self, cs_save_picture):
        cs.check_if_image_is_too_dark = Mock(return_value=False)
        get_brightness_threshold = Mock(return_value=0)
        get_retake_picam_pics_when_dark_setting = Mock(return_value=False)
        cs.get_group_document = Mock(return_value={})

        Picam.take_still = Mock()
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        normal_exposure_pic_id = uuid.uuid4()
        long_exposure_pic_id = uuid.uuid4()

        cs.take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id)

        picture_name = cs.build_picture_name(normal_exposure_pic_id)
        picture_path = cs.build_pic_path(picture_name)

        cs.save_picture.assert_called_once_with(
            {'_id': str(normal_exposure_pic_id),
             'type': 'picture',
             'source': 'picam',
             'exposure_type': 'standard',
             'group_id': str(group_id),
             'snap_id': str(snap_id),
             'filename': picture_name,
             'uri': ANY,
             'created': ANY
            }
        )

    @patch('camera.services.save_picture')
    def test_picam_still_saves_appropriate_long_exposure_picture_document(self, cs_save_picture):
        cs.check_if_image_is_too_dark = Mock(return_value=True)
        get_brightness_threshold = Mock(return_value=0)
        cs.get_retake_picam_pics_when_dark_setting = Mock(return_value=True)
        cs.get_group_document = Mock(return_value={})

        Picam.take_still = Mock()
        Picam.take_long_exposure_still = Mock()
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        normal_exposure_pic_id = uuid.uuid4()
        long_exposure_pic_id = uuid.uuid4()

        cs.take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id)

        long_exposure_picture_name = cs.build_picture_name(long_exposure_pic_id)
        long_exposure_picture_path = cs.build_pic_path(long_exposure_picture_name)

        call_1 = call(
                      {'_id': str(normal_exposure_pic_id),
                       'type': 'picture',
                       'source': 'picam',
                       'exposure_type': 'standard',
                       'group_id': str(group_id),
                       'snap_id': ANY,
                       'filename': ANY,
                       'uri': ANY,
                       'created': ANY
                      }
                     )
        call_2 = call(
                      {'_id': str(long_exposure_pic_id),
                       'type': 'picture',
                       'source': 'picam',
                       'exposure_type': 'long',
                       'group_id': str(group_id),
                       'snap_id': str(snap_id),
                       'filename': long_exposure_picture_name,
                       'uri': ANY,
                       'created': ANY
                      }
                     )

        calls = [call_1, call_2]
        cs_save_picture.assert_has_calls(calls)

    def test_picam_still_calls_picam_camera_class_as_expected_for_normal_exposure(self):
        Picam.take_still = Mock()
        cs.check_if_image_is_too_dark = Mock(return_value=False)
        get_brightness_threshold = Mock(return_value=0)
        get_retake_picam_pics_when_dark_setting = Mock(return_value=False)
        cs.get_group_document = Mock(return_value={})

        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        normal_exposure_pic_id = uuid.uuid4()
        long_exposure_pic_id = uuid.uuid4()

        cs.take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id)

        pic_doc = current_app.db[str(normal_exposure_pic_id)]
        picture_name = cs.build_picture_name(normal_exposure_pic_id)
        picture_path = cs.build_pic_path(picture_name)
        image_width = current_app.config['STILL_IMAGE_WIDTH']
        image_height = current_app.config['STILL_IMAGE_HEIGHT']

        Picam.take_still.assert_called_once_with(pic_path=picture_path,
                                                 image_width=image_width,
                                                 image_height=image_height)

    def test_picam_still_calls_picam_camera_class_as_expected_for_long_exposure(self):
        Picam.take_still = Mock()
        Picam.take_long_exposure_still = Mock()
        cs.check_if_image_is_too_dark = Mock(return_value=True)
        get_brightness_threshold = Mock(return_value=0)
        get_retake_picam_pics_when_dark_setting = Mock(return_value=True)
        cs.get_group_document = Mock(return_value={})

        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        normal_exposure_pic_id = uuid.uuid4()
        long_exposure_pic_id = uuid.uuid4()

        cs.take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id)

        picture_name = cs.build_picture_name(long_exposure_pic_id)
        picture_path = cs.build_pic_path(picture_name)
        image_width = current_app.config['STILL_IMAGE_WIDTH']
        image_height = current_app.config['STILL_IMAGE_HEIGHT']

        Picam.take_long_exposure_still.assert_called_once_with(pic_path=picture_path,
                                                               image_width=image_width,
                                                               image_height=image_height)
