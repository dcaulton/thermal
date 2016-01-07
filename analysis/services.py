import datetime
import os
import uuid

from flask import current_app
from PIL import Image, ImageStat, ImageOps

from admin.services import get_group_document
from thermal.appmodule import celery

def do_stuff():
    return {'analysis stuff': 'just got done'}

def check_if_image_is_too_dark(filename, brightness_threshold):
    image = Image.open(filename).convert('L')
    stat = ImageStat.Stat(image)
    avg_pixel_value = stat.mean[0]
    if avg_pixel_value < brightness_threshold:
        return True
    return False

@celery.task
def scale_image_chained(_, img_id_in, img_id_out):
    scale_image(img_id_in, img_id_out)

@celery.task
def scale_image(img_id_in, img_id_out):
# only works on black and white images for now
    group_document = get_group_document('current')
    (colorize_range_low, colorize_range_high) = ('#000080', '#FFD700')
    if 'colorize_range_low' in group_document and 'colorize_range_high' in group_document:
        colorize_range_low = group_document['colorize_range_low']
        colorize_range_high = group_document['colorize_range_high']
    img_dict_in = current_app.db[str(img_id_in)]
    img_filename_in = img_dict_in['filename']
    img_filename_out = "{0}.jpg".format(img_id_out)
    pic_path_in = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], img_filename_in)
    pic_path_out = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], img_filename_out)
    image_in = Image.open(pic_path_in)
    image_scaled = image_in.resize(
                        (current_app.config['STILL_IMAGE_WIDTH'], current_app.config['STILL_IMAGE_HEIGHT']),
                        Image.BICUBIC
                   )
    image_colorized = ImageOps.colorize(image_scaled, colorize_range_low, colorize_range_high)
    image_colorized.save(pic_path_out)
    img_dict_out = {
        'type': 'picture',
        'source': 'analysis',
        'source_image_id': str(img_id_in),
        'analysis_type': 'scale bicubic',
        'group_id': img_dict_in['group_id'],
        'snap_id': img_dict_in['snap_id'],
        'filename': img_filename_out,
        'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path_out),
        'created': str(datetime.datetime.now())
    }
    current_app.db[str(img_id_out)] = img_dict_out
