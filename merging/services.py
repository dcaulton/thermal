import datetime
import os
import uuid

from flask import current_app
from PIL import Image, ImageChops

def do_stuff():
    return {'merging stuff': 'just got done'}

def merge_images(img1_id_in, img2_id_in, img_id_out):
    img1_dict_in = current_app.db[str(img1_id_in)]
    img1_filename_in = img1_dict_in['filename']
    img2_dict_in = current_app.db[str(img2_id_in)]
    img2_filename_in = img2_dict_in['filename']
    img_filename_out = "{0}.jpg".format(str(img_id_out))
    pic1_path_in = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], img1_filename_in)
    pic2_path_in = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], img2_filename_in)
    pic_path_out = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], img_filename_out)
    image1_in = Image.open(pic1_path_in)
    image2_in = Image.open(pic2_path_in)
    image_out = ImageChops.screen(image1_in.convert('RGBA'), image2_in.convert('RGBA'))
    image_out.save(pic_path_out)

    img_dict_out = {
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
    current_app.db[str(img_id_out)] = img_dict_out
