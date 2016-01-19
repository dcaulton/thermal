from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import mock
import pytest 

from admin.services import clean_up_files, get_group_document, send_mail
from analysis.services import scale_image, distort_image_shepards_fixed
from merging.services import merge_images
import camera.views as cv

class TestViewsUnit(object):

#def picam_still():
#    snap_id = uuid.uuid4()
#    group_id = get_settings_document()['current_group_id']
#    delay = get_delay_parameter()
#    repeat = get_repeat_parameter()
#    ret_dict = take_picam_still(snap_id=snap_id, group_id=group_id, delay=delay, repeat=repeat)
#    return Response(json.dumps(ret_dict), status=202, mimetype='application/json')
#def thermal_still():
#    snap_id = uuid.uuid4()
#    group_id = get_settings_document()['current_group_id']
#    delay = get_delay_parameter()
#    repeat = get_repeat_parameter()
#    scale_image = get_scale_image_parameter()
#    ret_dict = take_thermal_still(snap_id=snap_id, group_id=group_id, delay=delay, repeat=repeat, scale_image=scale_image)
#    return Response(json.dumps(ret_dict), status=202, mimetype='application/json')
#def both_still():
#    snap_id = uuid.uuid4()
#    group_id = get_settings_document()['current_group_id']
#    delay = get_delay_parameter()
#    repeat = get_repeat_parameter()
#
#    both_still_dict = take_both_still(
#        snap_id=snap_id,
#        group_id=group_id,
#        delay=delay,
##        repeat=repeat
#    )
#
#    return Response(json.dumps(both_still_dict), status=202, mimetype='application/json')
#
#
#
#    @patch('admin.services.send_mail')
#    @patch('admin.services.clean_up_files')
#    @patch('analysis.services.scale_image')
#    @patch('camera.services.take_thermal_still')
#    def test_take_thermal_still_calls_all_chained_tasks(self,
#                                                        cs_take_thermal_still,
#                                                        ans_scale_image,
#                                                        ads_clean_up_files,
#                                                        ads_send_mail):
#        snap_id = uuid.uuid4()
#        group_id = get_group_document('current')['_id']
#        ct.take_thermal_still(snap_id=snap_id, group_id=group_id, delay=0, repeat=0)
#        cs_take_thermal_still.assert_called_once_with(snap_id, group_id, ANY)
#        ans_scale_image.assert_called_once_with(ANY, ANY, group_id)
#        ads_clean_up_files.assert_called_once_with(snap_id, group_id)
#        ads_send_mail.assert_called_once_with(snap_id, group_id)
