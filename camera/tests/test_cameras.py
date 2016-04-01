from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest

import camera.cameras as cc


class TestCameraUnit(object):


    @patch('camera.cameras.Picam.take_normal_exposure_still')
    def test_picam_take_still_calls_expected_methods(self,
                                                     ccp_take_normal_exposure_still):
        pc = cc.Picam()
        pc.take_still('the_pic_path', 123, 456)

        ccp_take_normal_exposure_still.assert_called_once_with(pic_path='the_pic_path',
                                                               image_width=123,
                                                               image_height=456)

    @patch('picamera.PiCamera')
    def test_take_normal_exposure_still_calls_expected_methods(self,
                                                               picamera_picamera):
        class MockCamera(object):
            def __init__(self):
                self.resolution = 0
                self.enter_called = False
                self.exit_called = False
                self.capture_called = False

            def __enter__(self):
                self.enter_called = True
                return self

            def __exit__(self, a, b, c):
                self.exit_called = True

            def capture(self):
                pass
        
        mock_camera = MockCamera()

        mock_camera.capture = Mock()

        picamera_picamera.return_value = mock_camera

        pc = cc.Picam()
        pc.take_normal_exposure_still('the_pic_path', 'the_image_width', 'the_image_height')

        mock_camera.capture.assert_called_once_with('the_pic_path')
        assert mock_camera.resolution == ('the_image_width', 'the_image_height')
        assert mock_camera.enter_called
        assert mock_camera.exit_called
