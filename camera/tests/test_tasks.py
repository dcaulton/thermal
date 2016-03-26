from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest

import admin.services
import admin.tasks
import camera.services
import camera.tasks as ct
from celery import Celery


class TestTasksUnit(object):

#    @patch('camera.tasks.picam_still_task.s')
#    @patch('camera.tasks.send_mail_chained.s')
#    @patch('camera.tasks.file_wrap_up_chained.s')
#    @patch('camera.tasks.chain')
#    def test_file_wrap_up_chained_calls_all_chained_tasks_no_repeat(self,
#                                                                    ct_chain,
#                                                                    ct_file_wrap_up_chained_s,
#                                                                    ct_send_mail_chained_s,
#                                                                    ct_picam_still_task_s):
#        snap_id = uuid.uuid4()
#        group_id = uuid.uuid4()
#        _ = None
#        ct.take_picam_still(snap_id, group_id, delay=0, repeat=0, clean_up_files=False)

#        assert ct_chain.mock_calls == [call(ct_picam_still_task_s()), call(ct_send_mail_chained_s()), call(ct_file_wrap_up_chained_s())]
#        ct_picam_still_task.assert_called_once_with(snap_id=snap_id,
#                                                    group_id=group_id,
#                                                    normal_exposure_pic_id=ANY,
#                                                    long_exposure_pic_id=ANY,
#                                                    clean_up_files=False)
#        at.file_wrap_up_chained(_, snap_id, group_id)
#        as_upload_files_to_s3.assert_called_once_with(snap_id, group_id)
#        as_clean_up_files.assert_called_once_with(snap_id, group_id)


    def test_take_picam_still_calls_expected_methods_with_defaults_for_delay_repeat_clean_up_files(self):
        camera.services.take_picam_still = Mock()
        admin.services.send_mail = Mock()
        admin.services.upload_files_to_s3 = Mock()
        admin.services.clean_up_files = Mock()

        return_value = ct.take_picam_still('some_snap_id', 'some_group_id')

        admin.services.send_mail.assert_called_once_with('some_snap_id', 'some_group_id')
        admin.services.upload_files_to_s3.assert_called_once_with('some_snap_id', 'some_group_id')
        admin.services.clean_up_files.assert_called_once_with('some_snap_id', 'some_group_id')
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
