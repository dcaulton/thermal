import uuid

from celery import chain

from admin.services import get_group_document
from admin.tasks import file_wrap_up_chained, send_mail_chained
from analysis.services import edge_detect_chained, scale_image_chained, distort_image_chained
import camera.services
from merging.services import merge_images_chained
from thermal.appmodule import celery


@celery.task
def take_picam_still_chained(_, snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id):
    '''
    Wrapper method to handle the celery scheduling of the taking of a single Picam still, with an extra parameter to handle
      how celery chains tasks.
    Calls the synchronous take_picam_still method.
    '''
    # don't call picam_still_task here.  It would cause a new celery task to be created, which would be out of
    #  sequence with the original chain of tasks we belong to
    camera.services.take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id)


def take_picam_still(snap_id, group_id, delay=0, repeat=0):
    '''
    Top level handler for taking Picam pictures between the camera view and the camera service modules.
    Besides group and snap information, it accepts get parameters to schedule delayed or repeating stills.
    '''
    normal_exposure_pic_ids = []
    long_exposure_pic_ids = []
    snap_ids = []
    for i in [x * delay for x in range(1, repeat + 2)]:
        normal_exposure_pic_id = uuid.uuid4()
        long_exposure_pic_id = uuid.uuid4()
        chain(
            picam_still_task.s(
                snap_id=snap_id,
                group_id=group_id,
                normal_exposure_pic_id=normal_exposure_pic_id,
                long_exposure_pic_id=long_exposure_pic_id
            ),
            send_mail_chained.s(
                snap_id=snap_id,
                group_id=group_id
            ),
            file_wrap_up_chained.s(
                snap_id=snap_id,
                group_id=group_id
            )
        ).apply_async(countdown=i)
        normal_exposure_pic_ids.append(str(normal_exposure_pic_id))
        long_exposure_pic_ids.append(str(long_exposure_pic_id))
        snap_ids.append(str(snap_id))
        snap_id = uuid.uuid4()
    return {
        'snap_ids': snap_ids,
        'group_id': str(group_id),
        'normal_exposure_pic_ids': normal_exposure_pic_ids,
        'long_exposure_pic_ids': long_exposure_pic_ids
    }


@celery.task
def picam_still_task(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id):
    '''
    Wrapper method to handle the celery scheduling of the taking of a single Picam still.
    Calls the synchronous take_picam_still method.
    '''
    camera.services.take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id)


def take_thermal_still(snap_id, group_id, delay=0, repeat=0, scale_image=True):
    '''
    Top level handler for taking Lepton pictures between the camera view and the camera service modules.
    Besides group and snap information, it accepts get parameters to schedule delayed or repeating stills.
    Also optionally accepts a parameter to chain an 'enlarge and colorize' task after the Lepton still if desired
    '''
    pic_ids = []
    scaled_pic_ids = []
    snap_ids = []
    if scale_image:
        for i in [x * delay for x in range(1, repeat + 2)]:
            pic_id = uuid.uuid4()
            scaled_pic_id = uuid.uuid4()
            chain(
                thermal_still_task.s(
                    snap_id=snap_id,
                    group_id=group_id,
                    pic_id=pic_id
                ),
                scale_image_chained.s(
                    img_id_in=pic_id,
                    img_id_out=scaled_pic_id,
                    group_id=group_id
                ),
                send_mail_chained.s(
                    snap_id=snap_id,
                    group_id=group_id
                ),
                file_wrap_up_chained.s(
                    snap_id=snap_id,
                    group_id=group_id
                )
            ).apply_async(countdown=i)
            pic_ids.append(str(pic_id))
            snap_ids.append(str(snap_id))
            scaled_pic_ids.append(str(scaled_pic_id))
            snap_id = uuid.uuid4()
    else:
        for i in [x * delay for x in range(1, repeat + 2)]:
            pic_id = uuid.uuid4()
            chain(
                thermal_still_task.s(
                    snap_id=snap_id,
                    group_id=group_id,
                    pic_id=pic_id
                ),
                send_mail_chained.s(
                    snap_id=snap_id,
                    group_id=group_id
                ),
                file_wrap_up_chained.s(
                    snap_id=snap_id,
                    group_id=group_id
                )
            ).apply_async(countdown=i)
            pic_ids.append(str(pic_id))
            snap_ids.append(str(snap_id))
            snap_id = uuid.uuid4()
    return {
        'pic_ids': pic_ids,
        'scaled_pic_ids': scaled_pic_ids,
        'snap_ids': snap_ids,
        'group_id': group_id
    }


@celery.task
def thermal_still_task(snap_id, group_id, pic_id):
    '''
    Wrapper method to handle the celery scheduling of the taking of a single Lepton still.
    Calls the synchronous take_thermal_still method.
    '''
    camera.services.take_thermal_still(snap_id, group_id, pic_id)


def take_both_still(snap_id, group_id, delay=0, repeat=0):
    '''
    Wrapper method to handle the celery scheduling of the taking of a 'both' still with standard subtasks.
    A both still and subtasks consists of:
      - Lepton still
      - Enlarge and colorize Lepton still
      - Distort enlarged+colorized Lepton still to compensate for lens distortion and alignment issues
      - Picam still
      - Merge picam still and 'Enlarged and colorized Lepton still'
      - Optionally email the result to recipients specified on the group file
    Calls the synchronous take_picam_still method.
    '''
    thermal_pic_ids = []
    normal_exposure_picam_pic_ids = []
    long_exposure_picam_pic_ids = []
    scaled_for_thermal_merge_pic_ids = []
    distorted_for_thermal_merge_pic_ids = []
    merged_pic_ids = []
    snap_ids = []

    for i in [x * delay for x in range(1, repeat + 2)]:
        thermal_pic_id = uuid.uuid4()
        normal_exposure_picam_pic_id = uuid.uuid4()
        long_exposure_picam_pic_id = uuid.uuid4()
        scaled_for_thermal_merge_pic_id = uuid.uuid4()
        distorted_for_thermal_merge_pic_id = uuid.uuid4()
        merged_pic_id = uuid.uuid4()
        chain(
            thermal_still_task.s(
                snap_id=snap_id,
                group_id=group_id,
                pic_id=thermal_pic_id
            ),
#            take_picam_still_chained.s(
#                snap_id=snap_id,
#                group_id=group_id,
#                normal_exposure_pic_id=normal_exposure_picam_pic_id,
#                long_exposure_pic_id=long_exposure_picam_pic_id
#            ),
#            scale_image_chained.s(
#                img_id_in=thermal_pic_id,
#                img_id_out=scaled_for_thermal_merge_pic_id,
#                group_id=group_id
#            ),
#            distort_image_chained.s(
#                img_id_in=scaled_for_thermal_merge_pic_id,
#                img_id_out=distorted_for_thermal_merge_pic_id,
#                group_id=group_id
#            ),
#            merge_images_chained.s(
#                img1_primary_id_in=normal_exposure_picam_pic_id,
#                img1_alternate_id_in=long_exposure_picam_pic_id,
#                img2_id_in=distorted_for_thermal_merge_pic_id,
#                img_id_out=merged_pic_id,
#                group_id=group_id
#            ),
#            send_mail_chained.s(
#                snap_id=snap_id,
#                group_id=group_id
#            ),
            file_wrap_up_chained.s(
                snap_id=snap_id,
                group_id=group_id
            )
        ).apply_async(countdown=i)
        thermal_pic_ids.append(str(thermal_pic_id))
        normal_exposure_picam_pic_ids.append(str(normal_exposure_picam_pic_id))
        long_exposure_picam_pic_ids.append(str(long_exposure_picam_pic_id))
        scaled_for_thermal_merge_pic_ids.append(str(scaled_for_thermal_merge_pic_id))
        distorted_for_thermal_merge_pic_ids.append(str(distorted_for_thermal_merge_pic_id))
        merged_pic_ids.append(str(merged_pic_id))
        snap_ids.append(str(snap_id))
        snap_id = uuid.uuid4()

    return {
        'snap_ids': snap_ids,
        'group_id': group_id,
        'normal_exposure_picam_ids': normal_exposure_picam_pic_ids,
        'long_exposure_picam_ids': long_exposure_picam_pic_ids,
        'thermal_ids': thermal_pic_ids,
        'scaled_for_thermal_merge_ids': scaled_for_thermal_merge_pic_ids,
        'distorted_for_thermal_merge_ids': distorted_for_thermal_merge_pic_ids,
        'merged_ids': merged_pic_ids
    }


#def take_both_still_test(snap_id, group_id, delay=0, repeat=0):
#    '''
#    Testing some fixed distortion logic
#    '''
#    thermal_pic_ids = []
#    normal_exposure_picam_pic_ids = []
#    long_exposure_picam_pic_ids = []
#    scaled_for_thermal_merge_pic_ids = []
#    distorted_for_thermal_merge_pic_ids = []
#    merged_pic_ids = []
#    snap_ids = []
#
#    for i in [x * delay for x in range(1, repeat + 2)]:
#        thermal_pic_id = uuid.uuid4()
#        normal_exposure_picam_pic_id = uuid.uuid4()
#        long_exposure_picam_pic_id = uuid.uuid4()
#        scaled_for_thermal_merge_pic_id = uuid.uuid4()
#        distorted_for_thermal_merge_pic_id = uuid.uuid4()
#        merged_pic_id = uuid.uuid4()
#        chain(
#            thermal_still_task.s(
#                snap_id=snap_id,
#                group_id=group_id,
#                pic_id=thermal_pic_id
#            ),
#            take_picam_still_chained.s(
#                snap_id=snap_id,
#                group_id=group_id,
#                normal_exposure_pic_id=normal_exposure_picam_pic_id,
#                long_exposure_pic_id=long_exposure_picam_pic_id
#            ),
#            scale_image_chained.s(
#                img_id_in=thermal_pic_id,
#                img_id_out=scaled_for_thermal_merge_pic_id,
#                group_id=group_id
#            ),
#            distort_image_chained.s(
#                img_id_in=scaled_for_thermal_merge_pic_id,
#                img_id_out=distorted_for_thermal_merge_pic_id,
#                group_id=group_id
#            ),
#            merge_images_chained.s(
#                img1_primary_id_in=normal_exposure_picam_pic_id,
#                img1_alternate_id_in=long_exposure_picam_pic_id,
#                img2_id_in=distorted_for_thermal_merge_pic_id,
#                img_id_out=merged_pic_id,
#                group_id=group_id
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
#        thermal_pic_ids.append(str(thermal_pic_id))
#        normal_exposure_picam_pic_ids.append(str(normal_exposure_picam_pic_id))
#        long_exposure_picam_pic_ids.append(str(long_exposure_picam_pic_id))
#        scaled_for_thermal_merge_pic_ids.append(str(scaled_for_thermal_merge_pic_id))
#        distorted_for_thermal_merge_pic_ids.append(str(distorted_for_thermal_merge_pic_id))
#        merged_pic_ids.append(str(merged_pic_id))
#        snap_ids.append(str(snap_id))
#        snap_id = uuid.uuid4()
#
#    return {
#        'snap_ids': snap_ids,
#        'group_id': group_id,
#        'normal_exposure_picam_ids': normal_exposure_picam_pic_ids,
#        'long_exposure_picam_ids': long_exposure_picam_pic_ids,
#        'thermal_ids': thermal_pic_ids,
#        'scaled_for_thermal_merge_ids': scaled_for_thermal_merge_pic_ids,
#        'distorted_for_thermal_merge_ids': distorted_for_thermal_merge_pic_ids,
#        'merged_ids': merged_pic_ids
#    }
#
#
#def take_both_still_edge_detect(snap_id, group_id, delay=0, repeat=0):
#    '''
#    Wrapper method to handle the celery scheduling of the taking of a 'both' still with standard subtasks.
#    A both still and subtasks consists of:
#      - Lepton still
#      - Enlarge and colorize Lepton still
#      - Picam still
#      - Merge picam still and 'Enlarged and colorized Lepton still'
#      - Optionally email the result to recipients specified on the group file
#    Calls the synchronous take_picam_still method.
#    '''
#    thermal_pic_ids = []
#    normal_exposure_picam_pic_ids = []
#    long_exposure_picam_pic_ids = []
#    scaled_for_thermal_merge_pic_ids = []
#    merged_pic_ids = []
#    picam_auto_pic_ids = []
#    picam_wide_pic_ids = []
#    picam_tight_pic_ids = []
#    thermal_auto_small_pic_ids = []
#    thermal_wide_small_pic_ids = []
#    thermal_tight_small_pic_ids = []
#    thermal_auto_large_pic_ids = []
#    thermal_wide_large_pic_ids = []
#    thermal_tight_large_pic_ids = []
#    snap_ids = []
#
#    for i in [x * delay for x in range(1, repeat + 2)]:
#        thermal_pic_id = uuid.uuid4()
#        normal_exposure_picam_pic_id = uuid.uuid4()
#        long_exposure_picam_pic_id = uuid.uuid4()
#        scaled_for_thermal_merge_pic_id = uuid.uuid4()
#        merged_pic_id = uuid.uuid4()
#        picam_auto_id = uuid.uuid4()
#        picam_wide_id = uuid.uuid4()
#        picam_tight_id = uuid.uuid4()
#        thermal_auto_small_id = uuid.uuid4()
#        thermal_wide_small_id = uuid.uuid4()
#        thermal_tight_small_id = uuid.uuid4()
#        thermal_auto_large_id = uuid.uuid4()
#        thermal_wide_large_id = uuid.uuid4()
#        thermal_tight_large_id = uuid.uuid4()
#        chain(
#            thermal_still_task.s(
#                snap_id=snap_id,
#                group_id=group_id,
#                pic_id=thermal_pic_id
#            ),
#            take_picam_still_chained.s(
#                snap_id=snap_id,
#                group_id=group_id,
#                normal_exposure_pic_id=normal_exposure_picam_pic_id,
#                long_exposure_pic_id=long_exposure_picam_pic_id
#            ),
#            edge_detect_chained.s(
#                img_id_in=normal_exposure_picam_pic_id,
#                alternate_img_id_in=long_exposure_picam_pic_id,
#                auto_id=picam_auto_id,
#                wide_id=picam_wide_id,
#                tight_id=picam_tight_id
#            ),
#            edge_detect_chained.s(
#                img_id_in=thermal_pic_id,
#                alternate_img_id_in='',
#                auto_id=thermal_auto_small_id,
#                wide_id=thermal_wide_small_id,
#                tight_id=thermal_tight_small_id
#            ),
#            scale_image_chained.s(
#                img_id_in=thermal_auto_small_id,
#                img_id_out=thermal_auto_large_id,
#                group_id=group_id,
#                scale_type='bicubic_blur'
#            ),
#            scale_image_chained.s(
#                img_id_in=thermal_wide_small_id,
#                img_id_out=thermal_wide_large_id,
#                group_id=group_id,
#                scale_type='bicubic_blur'
#            ),
#            scale_image_chained.s(
#                img_id_in=thermal_tight_small_id,
#                img_id_out=thermal_tight_large_id,
#                group_id=group_id,
#                scale_type='bicubic_blur'
#            ),
#            scale_image_chained.s(
#                img_id_in=thermal_pic_id,
#                img_id_out=scaled_for_thermal_merge_pic_id,
#                group_id=group_id,
#            ),
#            merge_images_chained.s(
#                img1_primary_id_in=normal_exposure_picam_pic_id,
#                img1_alternate_id_in=long_exposure_picam_pic_id,
#                img2_id_in=scaled_for_thermal_merge_pic_id,
#                img_id_out=merged_pic_id,
#                group_id=group_id
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
#        thermal_pic_ids.append(str(thermal_pic_id))
#        normal_exposure_picam_pic_ids.append(str(normal_exposure_picam_pic_id))
#        long_exposure_picam_pic_ids.append(str(long_exposure_picam_pic_id))
#        scaled_for_thermal_merge_pic_ids.append(str(scaled_for_thermal_merge_pic_id))
#        merged_pic_ids.append(str(merged_pic_id))
#        snap_ids.append(str(snap_id))
#        picam_auto_pic_ids.append(str(picam_auto_id))
#        picam_wide_pic_ids.append(str(picam_wide_id))
#        picam_tight_pic_ids.append(str(picam_tight_id))
#        thermal_auto_small_pic_ids.append(str(thermal_auto_small_id))
#        thermal_wide_small_pic_ids.append(str(thermal_wide_small_id))
#        thermal_tight_small_pic_ids.append(str(thermal_tight_small_id))
#        thermal_auto_large_pic_ids.append(str(thermal_auto_large_id))
#        thermal_wide_large_pic_ids.append(str(thermal_wide_large_id))
#        thermal_tight_large_pic_ids.append(str(thermal_tight_large_id))
#        snap_id = uuid.uuid4()
#
#    return {
#        'snap_ids': snap_ids,
#        'group_id': group_id,
#        'normal_exposure_picam_ids': normal_exposure_picam_pic_ids,
#        'long_exposure_picam_ids': long_exposure_picam_pic_ids,
#        'thermal_ids': thermal_pic_ids,
#        'scaled_for_thermal_merge_ids': scaled_for_thermal_merge_pic_ids,
#        'merged_ids': merged_pic_ids,
#        'picam_auto_pic_ids': picam_auto_pic_ids,
#        'picam_wide_pic_ids': picam_wide_pic_ids,
#        'picam_tight_pic_ids': picam_tight_pic_ids,
#        'thermal_auto_small_pic_ids': thermal_auto_small_pic_ids,
#        'thermal_wide_small_pic_ids': thermal_wide_small_pic_ids,
#        'thermal_tight_small_pic_ids': thermal_tight_small_pic_ids,
#        'thermal_auto_large_pic_ids': thermal_auto_large_pic_ids,
#        'thermal_wide_large_pic_ids': thermal_wide_large_pic_ids,
#        'thermal_tight_large_pic_ids': thermal_tight_large_pic_ids
#    }
