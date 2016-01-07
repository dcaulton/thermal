import uuid

from celery import chain

from admin.services import get_group_document
from analysis.services import scale_image_chained
import camera.services
from merging.services import merge_images_chained
from thermal.appmodule import celery

@celery.task
def take_picam_still_chained(_, snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id):
    # don't call picam_still_task here.  It would cause a new celery task to be created, which would be out of 
    #  sequence with the original chain of tasks we belong to
    camera.services.take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id)

def take_picam_still(snap_id, group_id, delay=0):
    normal_exposure_pic_id = uuid.uuid4()
    long_exposure_pic_id = uuid.uuid4()
    task = picam_still_task.apply_async(
        kwargs={
            'snap_id': snap_id,
            'group_id': group_id,
            'normal_exposure_pic_id': normal_exposure_pic_id,
            'long_exposure_pic_id': long_exposure_pic_id
        },
        countdown=delay
    )
    return {
        'snap_id': str(snap_id),
        'group_id': str(group_id),
        'normal_exposure_pic_id': str(normal_exposure_pic_id),
        'long_exposure_pic_id': str(long_exposure_pic_id)
    }

@celery.task
def picam_still_task(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id):
    camera.services.take_picam_still(snap_id, group_id, normal_exposure_pic_id, long_exposure_pic_id)

def take_thermal_still(snap_id, group_id, delay=0, scale_image=True):
    pic_id = uuid.uuid4()
    scaled_pic_id = uuid.uuid4()
    return_dict = {
        'snap_id': str(snap_id),
        'group_id': str(group_id),
        'pic_id': str(pic_id)
    }
    if scale_image:
        chain(
            thermal_still_task.s(
                snap_id=snap_id,
                group_id=group_id,
                pic_id=pic_id
            ),
            scale_image_chained.s(
                img_id_in=pic_id,
                img_id_out=scaled_pic_id
            )
        ).apply_async(countdown=delay)
        return_dict['scaled_pic_id'] = str(scaled_pic_id)
    else:
        thermal_still_task.apply_async(
            kwargs={
                'snap_id': snap_id,
                'group_id': group_id,
                'pic_id': pic_id
            },
            countdown=delay
        )
    return return_dict

@celery.task
def thermal_still_task(snap_id, group_id, pic_id):
    camera.services.take_thermal_still(snap_id, group_id, pic_id)

def both_still_chain(snap_id, group_id, delay=0):
    thermal_pic_id = uuid.uuid4()
    normal_exposure_picam_pic_id = uuid.uuid4()
    long_exposure_picam_pic_id = uuid.uuid4()
    scaled_pic_id = uuid.uuid4()
    merged_pic_id = uuid.uuid4()

    chain(
        thermal_still_task.s(
            snap_id=snap_id,
            group_id=group_id,
            pic_id=thermal_pic_id
        ),
        take_picam_still_chained.s(
            snap_id=snap_id,
            group_id=group_id,
            normal_exposure_pic_id=normal_exposure_picam_pic_id,
            long_exposure_pic_id=long_exposure_picam_pic_id
        ),
        scale_image_chained.s(
            img_id_in=thermal_pic_id,
            img_id_out=scaled_pic_id
        ),
        merge_images_chained.s(
            img1_primary_id_in=normal_exposure_picam_pic_id,
            img1_alternate_id_in=long_exposure_picam_pic_id,
            img2_id_in=scaled_pic_id,
            img_id_out=merged_pic_id
        )
    ).apply_async(countdown=delay)

    return {
        'snap_id': str(snap_id),
        'group_id': str(group_id),
        'normal_exposure_picam_id': str(normal_exposure_picam_pic_id),
        'long_exposure_picam_id': str(long_exposure_picam_pic_id),
        'thermal_id': str(thermal_pic_id),
        'scaled_id': str(scaled_pic_id),
        'merged_id': str(merged_pic_id)
    }
