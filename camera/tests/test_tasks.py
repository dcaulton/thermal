from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest

import camera.tasks as ct
from celery import Celery


class TestTasksUnit(object):
    pass

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




#def take_picam_still(snap_id, group_id, delay=0, repeat=0, clean_up_files=False):
#    '''
#    Top level handler for taking Picam pictures between the camera view and the camera service modules.
#    Besides group and snap information, it accepts get parameters to schedule delayed or repeating stills.
#    '''
#    normal_exposure_pic_ids = []
#    long_exposure_pic_ids = []
#    snap_ids = []
#    for i in [x * delay for x in range(1, repeat + 2)]:
#        normal_exposure_pic_id = uuid.uuid4()
#        long_exposure_pic_id = uuid.uuid4()
#        chain(
#            picam_still_task.s(
#                snap_id=snap_id,
#                group_id=group_id,
#                normal_exposure_pic_id=normal_exposure_pic_id,
#                long_exposure_pic_id=long_exposure_pic_id,
#                clean_up_files=clean_up_files
#            ),
#            send_mail_chained.s(
#                snap_id=snap_id,
#                group_id=group_id
#            ),
#            file_wrap_up_chained.s(
#                snap_id=snap_id,
#                group_id=group_id
#            )
#        ).apply_async(countdown=i)
#        normal_exposure_pic_ids.append(str(normal_exposure_pic_id))
#        long_exposure_pic_ids.append(str(long_exposure_pic_id))
#        snap_ids.append(str(snap_id))
#        snap_id = uuid.uuid4()
#    return {
#        'snap_ids': snap_ids,
#        'group_id': str(group_id),
#        'normal_exposure_pic_ids': normal_exposure_pic_ids,
#        'long_exposure_pic_ids': long_exposure_pic_ids
#    }

