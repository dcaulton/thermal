from celery import chain
from flask import current_app

import admin.services
from thermal.appmodule import celery, mail
from thermal.utils import log_asynchronous_exception


@celery.task
def upload_files_to_s3_task(snap_id, group_id):
    try:
        admin.services.upload_files_to_s3(snap_id, group_id)
    except Exception as e:
        log_asynchronous_exception(e)


@celery.task
def file_wrap_up_chained(_, snap_id, group_id):
    chain(
        upload_files_to_s3_task.s(
            snap_id=snap_id,
            group_id=group_id
        ),
        clean_up_files_chained.s(
            snap_id=snap_id,
            group_id=group_id
        )
    ).apply_async()


@celery.task
def clean_up_files_task(snap_id, group_id):
    try:
        admin.services.clean_up_files(snap_id, group_id)
    except Exception as e:
        log_asynchronous_exception(e)

@celery.task
def clean_up_files_chained(_, snap_id, group_id):
    try:
        admin.services.clean_up_files(snap_id, group_id)
    except Exception as e:
        log_asynchronous_exception(e)


@celery.task
def send_mail_chained(_, snap_id, group_id):
    try:
        admin.services.send_mail(snap_id, group_id)
    except Exception as e:
        log_asynchronous_exception(e)
