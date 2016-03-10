import os

from flask import current_app


def build_picture_path(picture_name, snap_id='', create_directory=True):
    pictures_directory = current_app.config['PICTURE_SAVE_DIRECTORY']
    temp_directory = os.path.join(pictures_directory, str(snap_id))
    if create_directory and not os.path.isdir(temp_directory):
        os.mkdir(temp_directory)
    return os.path.join(temp_directory, picture_name)


def build_picture_name(pic_id):
    return "{0}.jpg".format(pic_id)
