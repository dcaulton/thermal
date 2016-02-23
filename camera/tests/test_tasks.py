from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest

from admin.services import clean_up_files, get_group_document, send_mail
from analysis.services import scale_image, distort_image_shepards_fixed
from merging.services import merge_images
import camera.tasks as ct
from camera.services import take_picam_still, take_thermal_still


class TestTasksUnit(object):

    @patch('admin.services.send_mail')
    @patch('admin.services.clean_up_files')
    @patch('camera.services.take_picam_still')
    def test_picam_still_calls_all_chained_tasks(self, cs_take_picam_still, as_clean_up_files, as_send_mail):
        snap_id = uuid.uuid4()
        group_id = get_group_document('current')['_id']
        ct.take_picam_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=0)
        cs_take_picam_still.assert_called_once_with(snap_id, group_id, ANY, ANY)
        as_clean_up_files.assert_called_once_with(snap_id, group_id)
        as_send_mail.assert_called_once_with(snap_id, group_id)

    @patch('admin.services.send_mail')
    @patch('admin.services.clean_up_files')
    @patch('camera.services.take_picam_still')
    def test_picam_still_calls_all_chained_tasks_multiple_times_when_repeat_specified(self,
                                                                                      cs_take_picam_still,
                                                                                      as_clean_up_files,
                                                                                      as_send_mail):
        snap_id = uuid.uuid4()
        group_id = get_group_document('current')['_id']
        ct.take_picam_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=2)
        tps_calls = [call(snap_id, group_id, ANY, ANY), call(ANY, group_id, ANY, ANY), call(ANY, group_id, ANY, ANY)]
        ascuf_calls = [call(snap_id, group_id), call(ANY, group_id), call(ANY, group_id)]
        assm_calls = [call(snap_id, group_id), call(ANY, group_id), call(ANY, group_id)]
        cs_take_picam_still.assert_has_calls(tps_calls)
        as_clean_up_files.assert_has_calls(ascuf_calls)
        as_send_mail.assert_has_calls(assm_calls)

    @patch('admin.services.send_mail')
    @patch('admin.services.clean_up_files')
    @patch('analysis.services.scale_image')
    @patch('camera.services.take_thermal_still')
    def test_take_thermal_still_calls_all_chained_tasks(self,
                                                        cs_take_thermal_still,
                                                        ans_scale_image,
                                                        ads_clean_up_files,
                                                        ads_send_mail):
        snap_id = uuid.uuid4()
        group_id = get_group_document('current')['_id']
        ct.take_thermal_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=0)
        cs_take_thermal_still.assert_called_once_with(snap_id, group_id, ANY)
        ans_scale_image.assert_called_once_with(ANY, ANY, group_id)
        ads_clean_up_files.assert_called_once_with(snap_id, group_id)
        ads_send_mail.assert_called_once_with(snap_id, group_id)

    @patch('admin.services.send_mail')
    @patch('admin.services.clean_up_files')
    @patch('analysis.services.scale_image')
    @patch('camera.services.take_thermal_still')
    def test_take_thermal_still_calls_all_chained_tasks_multiple_times_when_repeat_specified(self,
                                                                                             cs_take_thermal_still,
                                                                                             ans_scale_image,
                                                                                             ads_clean_up_files,
                                                                                             ads_send_mail):
        snap_id = uuid.uuid4()
        group_id = get_group_document('current')['_id']
        ct.take_thermal_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=1)
        cs_take_thermal_still.assert_has_calls([call(snap_id, group_id, ANY), call(ANY, group_id, ANY)])
        ans_scale_image.assert_has_calls([call(ANY, ANY, group_id), call(ANY, ANY, group_id)])
        ads_send_mail.assert_has_calls([call(snap_id, group_id), call(ANY, group_id)])
        ads_clean_up_files.assert_has_calls([call(snap_id, group_id), call(ANY, group_id)])

    @patch('admin.services.send_mail')
    @patch('admin.services.clean_up_files')
    @patch('analysis.services.scale_image')
    @patch('camera.services.take_thermal_still')
    def test_take_thermal_still_skips_scale_image_when_requested(self,
                                                                 cs_take_thermal_still,
                                                                 ans_scale_image,
                                                                 ads_clean_up_files,
                                                                 ads_send_mail):
        snap_id = uuid.uuid4()
        group_id = get_group_document('current')['_id']
        ct.take_thermal_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=0, scale_image=False)
        cs_take_thermal_still.assert_called_once_with(snap_id, group_id, ANY)
        ans_scale_image.assert_not_called()
        ads_send_mail.assert_called_once_with(snap_id, group_id)
        ads_clean_up_files.assert_called_once_with(snap_id, group_id)

    @patch('admin.services.send_mail')
    @patch('admin.services.clean_up_files')
    @patch('merging.services.merge_images')
    @patch('analysis.services.distort_image_shepards_fixed')
    @patch('analysis.services.scale_image')
    @patch('camera.services.take_thermal_still')
    @patch('camera.services.take_picam_still')
    def test_take_both_still_calls_all_chained_tasks(self,
                                                     cs_take_picam_still,
                                                     cs_take_thermal_still,
                                                     ans_scale_image,
                                                     ans_distort_image_shepards_fixed,
                                                     ms_merge_image,
                                                     ads_clean_up_files,
                                                     ads_send_mail):
        snap_id = uuid.uuid4()
        group_id = get_group_document('current')['_id']
        ct.take_both_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=0)
        cs_take_thermal_still.assert_called_once_with(snap_id, group_id, ANY)
        cs_take_picam_still.assert_called_once_with(snap_id, group_id, ANY, ANY)
        ans_scale_image.assert_called_once_with(ANY, ANY, group_id)
        ans_distort_image_shepards_fixed.assert_called_once_with(ANY, ANY, group_id)
        ms_merge_image.assert_called_once_with(ANY, ANY, ANY, ANY, group_id)
        ads_send_mail.assert_called_once_with(snap_id, group_id)
        ads_clean_up_files.assert_called_once_with(snap_id, group_id)

    @patch('admin.services.send_mail')
    @patch('admin.services.clean_up_files')
    @patch('merging.services.merge_images')
    @patch('analysis.services.distort_image_shepards_fixed')
    @patch('analysis.services.scale_image')
    @patch('camera.services.take_thermal_still')
    @patch('camera.services.take_picam_still')
    def test_take_both_still_calls_all_chained_tasks_multiple_times_when_repeat_specified(self,
                                                                                          cs_take_picam_still,
                                                                                          cs_take_thermal_still,
                                                                                          ans_scale_image,
                                                                                          ans_distort_image_shepards_fixed,
                                                                                          ms_merge_image,
                                                                                          ads_clean_up_files,
                                                                                          ads_send_mail):
        snap_id = uuid.uuid4()
        group_id = get_group_document('current')['_id']
        ct.take_both_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=1)
        cs_take_thermal_still.assert_has_calls([call(snap_id, group_id, ANY), call(ANY, group_id, ANY)])
        cs_take_picam_still.assert_has_calls([call(snap_id, group_id, ANY, ANY), call(ANY, group_id, ANY, ANY)])
        ans_scale_image.assert_has_calls([call(ANY, ANY, group_id), call(ANY, ANY, group_id)])
        ans_distort_image_shepards_fixed.assert_has_calls([call(ANY, ANY, group_id), call(ANY, ANY, group_id)])
        ms_merge_image.assert_has_calls([call(ANY, ANY, ANY, ANY, group_id), call(ANY, ANY, ANY, ANY, group_id)])
        ads_send_mail.assert_has_calls([call(snap_id, group_id), call(ANY, group_id)])
        ads_clean_up_files.assert_has_calls([call(snap_id, group_id), call(ANY, group_id)])
