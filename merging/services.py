import datetime
import uuid

from flask import current_app
from PIL import Image, ImageChops

from admin.services import get_group_document
from picture.services import (build_picture_path,
                              build_picture_name)
from thermal.appmodule import celery
from thermal.services import save_generic
from thermal.utils import (get_document_with_exception,
                           item_exists,
                           log_asynchronous_exception)


@celery.task
def merge_images_chained(_, img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out, group_id):
    try:
        merge_images(img1_primary_id_in=img1_primary_id_in,
                     img1_alternate_id_in=img1_alternate_id_in,
                     img2_id_in=img2_id_in,
                     img_id_out=img_id_out,
                     group_id=group_id)
    except Exception as e:
        log_asynchronous_exception(e)


@celery.task
def merge_images_task(img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out, group_id, **kwargs):
    try:
        merge_images(img1_primary_id_in=img1_primary_id_in,
                     img1_alternate_id_in=img1_alternate_id_in,
                     img2_id_in=img2_id_in,
                     img_id_out=img_id_out,
                     group_id=group_id,
                     **kwargs)
    except Exception as e:
        log_asynchronous_exception(e)


def get_image_paths_and_snap_id(img1_id_in, img2_id_in, img_id_out):
    img1_dict_in = get_document_with_exception(str(img1_id_in), 'picture')
    img1_filename_in = img1_dict_in['filename']
    img2_dict_in = get_document_with_exception(str(img2_id_in), 'picture')
    img2_filename_in = img2_dict_in['filename']
    img_filename_out = build_picture_name(img_id_out)
    pic1_path_in = build_picture_path(picture_name=img1_filename_in, snap_id=img1_dict_in['snap_id'])
    pic2_path_in = build_picture_path(picture_name=img2_filename_in, snap_id=img1_dict_in['snap_id'])
    pic_path_out = build_picture_path(picture_name=img_filename_out, snap_id=img1_dict_in['snap_id'])
    return {'img1_path': pic1_path_in,
            'img2_path': pic2_path_in,
            'img_out_path': pic_path_out,
            'img_out_filename': img_filename_out,
            'snap_id': img1_dict_in['snap_id']}

def merge_type_is_valid(merge_type):
    if hasattr(ImageChops, merge_type):
        return True
    return False

def get_merge_method(merge_type):
    if merge_type_is_valid(merge_type):
        return getattr(ImageChops, merge_type)
    else:
        return getattr(ImageChops, 'screen')

def do_image_merge(paths_dict, merge_method):
    image1_in = Image.open(paths_dict['img1_path'])
    image2_in = Image.open(paths_dict['img2_path'])
    image_out = merge_method(image1_in.convert('RGBA'), image2_in.convert('RGBA'))
    image_out.save(paths_dict['img_out_path'])

def get_merge_type(group_id, **kwargs):
    if 'merge_type' in kwargs and kwargs['merge_type']:
        merge_type = kwargs['merge_type']
        print 'getting merge type from kwargs: '+merge_type
    else:
        group_document = get_group_document(group_id)
        if 'merge_type' in group_document:
            merge_type = group_document['merge_type']
            print 'getting merge type from group_doc: '+merge_type
        else:
            merge_type = 'screen'
            print 'defaulting merge type to screen'
    return merge_type

def merge_images(img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out, group_id, **kwargs):
    # TODO deal more elegantly with the fact that different merge methods require different parameters
    # the assumption is that the merged picture will be saved in the directory with the snap of image 1
    # it also assumes that both images have not yet been deleted with clean_up_files
        merge_type = get_merge_type(group_id, **kwargs)
        merge_method = get_merge_method(merge_type)

        img1_id_in = img1_primary_id_in
        if item_exists(img1_alternate_id_in, 'picture'):
            img1_id_in = img1_alternate_id_in

        paths_dict = get_image_paths_and_snap_id(img1_id_in, img2_id_in, img_id_out)

        do_image_merge(paths_dict, merge_method)

        img_dict_out = {
            '_id': str(img_id_out),
            'type': 'picture',
            'source': 'merge',
            'source_image_id_1': str(img1_id_in),
            'source_image_id_2': str(img2_id_in),
            'merge_type': merge_type,
            'group_id': group_id,
            'snap_id': paths_dict['snap_id'],
            'filename': paths_dict['img_out_filename'],
            'uri': paths_dict['img_out_path'],
            'created': str(datetime.datetime.now())
        }
        save_generic(img_dict_out, 'picture')
