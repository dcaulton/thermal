import datetime
import os
import uuid

from flask import current_app
from PIL import Image, ImageChops

from admin.services import get_group_document
from picture.services import find_picture, save_picture_document
from thermal.appmodule import celery


def do_stuff():
    return {'merging stuff': 'just got done'}

@celery.task
def merge_images_chained(_, img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out):
    merge_images(img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out)

@celery.task
def merge_images_task(img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out):
    merge_images(img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out)

def merge_images(img1_primary_id_in, img1_alternate_id_in, img2_id_in, img_id_out):
    #deal with the fact that different merge methods require different parameters
    group_document = get_group_document('current')

    img1_id_in = img1_primary_id_in
    if str(img1_alternate_id_in) in current_app.db:
        img1_id_in = img1_alternate_id_in

    if 'merge_type' in group_document:
        merge_type = group_document['merge_type']

    if hasattr(ImageChops, merge_type):
        merge_method = getattr(ImageChops, merge_type)
    else:
        merge_method = getattr(ImageChops, 'screen')

    img1_dict_in = find_picture(str(img1_id_in))
    img1_filename_in = img1_dict_in['filename']
    img2_dict_in = find_picture(str(img2_id_in))
    img2_filename_in = img2_dict_in['filename']
    img_filename_out = build_picture_name(img_id_out)
    pic1_path_in = build_picture_path(img1_filename_in)
    pic2_path_in = build_picture_path(img2_filename_in)
    pic_path_out = build_picture_path(img_filename_out)
    image1_in = Image.open(pic1_path_in)
    image2_in = Image.open(pic2_path_in)
    image_out = merge_method(image1_in.convert('RGBA'), image2_in.convert('RGBA'))
    image_out.save(pic_path_out)

    img_dict_out = {
        '_id': str(img_id_out),
        'type': 'picture',
        'source': 'merge',
        'source_image_id_1': str(img1_id_in),
        'source_image_id_2': str(img2_id_in),
        'merge_type': 'screen',
        'group_id': img1_dict_in['group_id'],
        'snap_id': img1_dict_in['snap_id'],
        'filename': img_filename_out,
        'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path_out),
        'created': str(datetime.datetime.now())
    }
    save_picture_document(img_dict_out)

def build_picture_name(picture_id):
    return "{0}.jpg".format(picture_id)

def build_picture_path(picture_name):
    return os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], picture_name)
