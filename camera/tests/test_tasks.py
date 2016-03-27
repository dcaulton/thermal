from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest

import admin.services
import analysis.services
import admin.tasks
import camera.services
import camera.tasks as ct
from celery import Celery
from thermal.exceptions import ThermalBaseError


class TestTasksUnit(object):

    def test_take_picam_still_calls_expected_methods_with_defaults_for_delay_repeat_clean_up_files(self):
        camera.services.take_picam_still = Mock()
        admin.services.send_mail = Mock()
        admin.services.upload_files_to_s3 = Mock()
        admin.services.clean_up_files = Mock()

        return_value = ct.take_picam_still('some_snap_id', 'some_group_id')

        camera.services.take_picam_still.assert_called_once_with('some_snap_id', 'some_group_id', ANY, ANY, True)

        admin.services.send_mail.assert_called_once_with('some_snap_id', 'some_group_id')
        admin.services.upload_files_to_s3.assert_called_once_with('some_snap_id', 'some_group_id')
        admin.services.clean_up_files.assert_called_once_with('some_snap_id', 'some_group_id')
        assert return_value == {'snap_ids': ['some_snap_id'],
                                'group_id': 'some_group_id',
                                'normal_exposure_pic_ids': [ANY],
                                'long_exposure_pic_ids': [ANY]}

    def test_take_picam_still_calls_expected_methods_with_expected_values_when_clean_up_files_is_off(self):
        camera.services.take_picam_still = Mock()
        admin.services.send_mail = Mock()
        admin.services.upload_files_to_s3 = Mock()
        admin.services.clean_up_files = Mock()

        return_value = ct.take_picam_still('some_snap_id', 'some_group_id', clean_up_files=False)

        camera.services.take_picam_still.assert_called_once_with('some_snap_id', 'some_group_id', ANY, ANY, False)

        assert return_value == {'snap_ids': ['some_snap_id'],
                                'group_id': 'some_group_id',
                                'normal_exposure_pic_ids': [ANY],
                                'long_exposure_pic_ids': [ANY]}

    def test_take_picam_still_calls_expected_methods_with_nonzero_repeat(self):
        camera.services.take_picam_still = Mock()
        admin.services.send_mail = Mock()
        admin.services.upload_files_to_s3 = Mock()
        admin.services.clean_up_files = Mock()

        return_value = ct.take_picam_still('some_snap_id', 'some_group_id', delay=0, repeat=2)

        admin.services.send_mail.assert_has_calls([call('some_snap_id', 'some_group_id'),
                                                   call(ANY, 'some_group_id')])
        admin.services.upload_files_to_s3.assert_has_calls([call('some_snap_id', 'some_group_id'),
                                                            call(ANY, 'some_group_id')])
        admin.services.clean_up_files.assert_has_calls([call('some_snap_id', 'some_group_id'),
                                                        call(ANY, 'some_group_id')])
        assert return_value == {'snap_ids': ['some_snap_id', ANY, ANY],
                                'group_id': 'some_group_id',
                                'normal_exposure_pic_ids': [ANY, ANY, ANY],
                                'long_exposure_pic_ids': [ANY, ANY, ANY]}

    def test_take_thermal_still_calls_expected_methods_with_defaults_for_delay_repeat_and_clean_up_files_on(self):
        camera.services.take_thermal_still = Mock()
        analysis.services.scale_image = Mock()
        admin.services.send_mail = Mock()
        admin.services.upload_files_to_s3 = Mock()
        admin.services.clean_up_files = Mock()

        return_value = ct.take_thermal_still('some_snap_id', 'some_group_id')

        camera.services.take_thermal_still.assert_called_once_with('some_snap_id', 'some_group_id', ANY, True)
        analysis.services.scale_image.assert_called_once_with(ANY, ANY, 'some_group_id', scale_image=True)
        admin.services.send_mail.assert_called_once_with('some_snap_id', 'some_group_id')
        admin.services.upload_files_to_s3.assert_called_once_with('some_snap_id', 'some_group_id')
        admin.services.clean_up_files.assert_called_once_with('some_snap_id', 'some_group_id')
        assert return_value == {'snap_ids': ['some_snap_id'],
                                'group_id': 'some_group_id',
                                'pic_ids': [ANY],
                                'scaled_pic_ids': [ANY]}

    def test_take_thermal_still_calls_expected_methods_with_expected_values_when_clean_up_files_of(self):
        camera.services.take_thermal_still = Mock()
        analysis.services.scale_image = Mock()
        admin.services.send_mail = Mock()
        admin.services.upload_files_to_s3 = Mock()
        admin.services.clean_up_files = Mock()

        return_value = ct.take_thermal_still('some_snap_id', 'some_group_id', clean_up_files=False)

        camera.services.take_thermal_still.assert_called_once_with('some_snap_id', 'some_group_id', ANY, False)
        assert return_value == {'snap_ids': ['some_snap_id'],
                                'group_id': 'some_group_id',
                                'pic_ids': [ANY],
                                'scaled_pic_ids': [ANY]}

    def test_take_thermal_still_calls_expected_methods_with_nonzero_for_repeat(self):
        camera.services.take_thermal_still = Mock()
        analysis.services.scale_image = Mock()
        admin.services.send_mail = Mock()
        admin.services.upload_files_to_s3 = Mock()
        admin.services.clean_up_files = Mock()

        return_value = ct.take_thermal_still('some_snap_id', 'some_group_id', delay=0, repeat=1)

        camera.services.take_thermal_still.assert_has_calls([call('some_snap_id', 'some_group_id', ANY, True),
                                                             call(ANY, 'some_group_id', ANY, True)])
        analysis.services.scale_image.assert_has_calls([call(ANY, ANY, 'some_group_id', scale_image=True),
                                                        call(ANY, ANY, 'some_group_id', scale_image=True)])
        admin.services.send_mail.assert_has_calls([call('some_snap_id', 'some_group_id'),
                                                   call(ANY, 'some_group_id')])
        admin.services.upload_files_to_s3.assert_has_calls([call('some_snap_id', 'some_group_id'),
                                                            call(ANY, 'some_group_id')])
        admin.services.clean_up_files.assert_has_calls([call('some_snap_id', 'some_group_id'),
                                                        call(ANY, 'some_group_id')])
        assert return_value == {'snap_ids': ['some_snap_id', ANY],
                                'group_id': 'some_group_id',
                                'pic_ids': [ANY, ANY],
                                'scaled_pic_ids': [ANY, ANY]}

    def test_take_thermal_still_calls_expected_methods_with_scale_image_turned_off(self):
        camera.services.take_thermal_still = Mock()
        analysis.services.scale_image = Mock()
        admin.services.send_mail = Mock()
        admin.services.upload_files_to_s3 = Mock()
        admin.services.clean_up_files = Mock()

        return_value = ct.take_thermal_still('some_snap_id', 'some_group_id', scale_image=False)

        camera.services.take_thermal_still.assert_called_once_with('some_snap_id', 'some_group_id', ANY, True)
        analysis.services.scale_image.assert_not_called()
        admin.services.send_mail.assert_called_once_with('some_snap_id', 'some_group_id')
        admin.services.upload_files_to_s3.assert_called_once_with('some_snap_id', 'some_group_id')
        admin.services.clean_up_files.assert_called_once_with('some_snap_id', 'some_group_id')
        assert return_value == {'snap_ids': ['some_snap_id'],
                                'group_id': 'some_group_id',
                                'pic_ids': [ANY],
                                'scaled_pic_ids': []}





    @patch('camera.tasks.log_asynchronous_exception')
    @patch('camera.services.take_picam_still')
    def test_take_picam_still_chained_catches_exception(self,
                                                        cs_take_picam_still,
                                                        ct_log_asynchronous_exception):
        the_exception = ThermalBaseError('steve_wilkos')
        cs_take_picam_still.side_effect = the_exception

        ct.take_picam_still_chained('a', 'b', 'c', 'd', 'e', 'f')

        cs_take_picam_still.assert_called_once_with('b', 'c', 'd', 'e', 'f')
        ct_log_asynchronous_exception.assert_called_once_with(the_exception)

    @patch('camera.tasks.log_asynchronous_exception')
    @patch('camera.services.take_picam_still')
    def test_picam_still_task_catches_exception(self,
                                                cs_take_picam_still,
                                                ct_log_asynchronous_exception):
        the_exception = ThermalBaseError('wendy_williams')
        cs_take_picam_still.side_effect = the_exception

        ct.picam_still_task('a', 'b', 'c', 'd', 'e')

        cs_take_picam_still.assert_called_once_with('a', 'b', 'c', 'd', 'e')
        ct_log_asynchronous_exception.assert_called_once_with(the_exception)

    @patch('camera.tasks.log_asynchronous_exception')
    @patch('camera.services.take_thermal_still')
    def test_thermal_still_task_catches_exception(self,
                                                  cs_take_thermal_still,
                                                  ct_log_asynchronous_exception):
        the_exception = ThermalBaseError('bill_cunningham')
        cs_take_thermal_still.side_effect = the_exception

        ct.thermal_still_task('a', 'b', 'c', 'd')

        cs_take_thermal_still.assert_called_once_with('a', 'b', 'c', 'd')
        ct_log_asynchronous_exception.assert_called_once_with(the_exception)
