import datetime
import os
import uuid

from flask import current_app
from PIL import Image, ImageOps

def do_stuff():
    return {'analysis stuff': 'just got done'}

def scale_image(img_id_in):
    img_id_out = uuid.uuid4()
    img_dict_in = current_app.db[str(img_id_in)]
    img_filename_in = img_dict_in['filename']
    img_filename_out = "{0}-scaled.jpg".format(img_dict_in['_id'])
    pic_path_in = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], img_filename_in)
    pic_path_out = os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], img_filename_out)
    image_in = Image.open(pic_path_in)
    image_scaled = image_in.resize(
                        (current_app.config['STILL_IMAGE_WIDTH'], current_app.config['STILL_IMAGE_HEIGHT']),
                        Image.BICUBIC
                   )
    image_colorized = ImageOps.colorize(image_scaled, '#000080', '#FFD700')
    image_colorized.save(pic_path_out)
    img_dict_out = {
        'type': 'picture',
        'camera_type': 'analysis',
        'source_image_id': str(img_id_in),
        'analysis_type': 'scale bicubic',
        'group_id': img_dict_in['group_id'],
        'snap_id': img_dict_in['snap_id'],
        'filename': img_filename_out,
        'uri': "file://{0}{1}".format(current_app.config['HOSTNAME'], pic_path_out),
        'created': str(datetime.datetime.now())
    }
    current_app.db[str(img_id_out)] = img_dict_out
