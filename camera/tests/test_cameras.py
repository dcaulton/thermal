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

# TODO gonna have to mock a context manager here.  
#       THIS MIGHT HELP?  http://stackoverflow.com/questions/1289894/how-do-i-mock-an-open-used-in-a-with-statement-using-the-mock-framework-in-pyth
#    @patch('picamera.PiCamera')
#    def test_take_normal_exposure_still_calls_expected_methods(self,
#                                                               picamera_picamera):
#        class MockCamera(object):
#            pass
#        mock_camera = MockCamera()
#        mock_camera.capture = Mock()
#
#        picamera_picamera.return_value = mock_camera
#
#        pc = cc.Picam()
#        pc.take_normal_exposure_still('the_pic_path', 'the_image_width', 'the_image_height')
#
##            camera.resolution = (image_width, image_height)
#        mock_camera.capture.assert_called_once_with('the_pic_path')
