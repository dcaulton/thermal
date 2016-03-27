from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest

import admin.tasks as admt
from admin.services import clean_up_files, send_mail, upload_files_to_s3


class TestTasksUnit(object):

    @patch('admin.services.upload_files_to_s3')
    @patch('admin.services.clean_up_files')
    def test_file_wrap_up_chained_calls_all_chained_tasks(self, as_clean_up_files, as_upload_files_to_s3):
        snap_id = uuid.uuid4()
        group_id = uuid.uuid4()
        _ = None
        admt.file_wrap_up_chained(_, snap_id, group_id)
        as_upload_files_to_s3.assert_called_once_with(snap_id, group_id)
        as_clean_up_files.assert_called_once_with(snap_id, group_id)

    @patch('admin.services.clean_up_files')
    def test_clean_up_files_task_calls_expected_methods(self,
                                                        as_clean_up_files):
        admt.clean_up_files_task('a', 'b')
        as_clean_up_files.assert_called_once_with('a', 'b')
    
    @patch('admin.services.send_mail')
    def test_send_mail_chained_calls_expected_methods(self,
                                                      as_send_mail):
        admt.send_mail_chained('a', 'b', 'c')
        as_send_mail.assert_called_once_with('b', 'c')
