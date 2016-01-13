from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
from PIL import Image, ImageStat, ImageOps
import pytest 

from admin.services import get_group_document
import analysis.services as ans
from picture.services import build_picture_path, find_picture, save_picture_document
from thermal.appmodule import celery

class TestServicesUnit(object):
 
    def test_scale_image(self):
        class MockImage(object):
            pass

        group_id = uuid.uuid4()
        snap_id = uuid.uuid4()
        ans.save_picture_document = Mock()
        the_picture_path = build_picture_path(picture_name='whatever', snap_id=snap_id, create_directory=False)
        ans.find_picture = Mock(return_value={'filename': 'whatever',
                                              'group_id': str(group_id),
                                              'snap_id': str(snap_id),
                                              'uri': the_picture_path
                                             }
                           )
        ans.get_group_document = Mock(return_value={
                                  'colorize_range_low': 1.1,
                                  'colorize_range_high': 2.2
                                  }
                                 )
        the_mock_image = MockImage()
        Image.open = Mock(return_value=the_mock_image)
        MockImage.resize = Mock(return_value=the_mock_image)
        MockImage.save = Mock()
        ImageOps.colorize = Mock(return_value=the_mock_image)
        img_id_in = uuid.uuid4()
        img_id_out = uuid.uuid4()
        image_width = current_app.config['STILL_IMAGE_WIDTH']
        image_height = current_app.config['STILL_IMAGE_HEIGHT']
        img_filename_out = ans.build_picture_name(img_id_out)
        pic_path_out = ans.build_picture_path(picture_name=img_filename_out, snap_id=snap_id)
        test_img_dict_out = {
            '_id': str(img_id_out),
            'type': 'picture',
            'source': 'analysis',
            'source_image_id': str(img_id_in),
            'analysis_type': 'colorize_bicubic',
            'group_id': str(group_id),
            'snap_id': str(snap_id),
            'filename': img_filename_out,
            'uri': ANY,
            'created': ANY
        }

        ans.scale_image(img_id_in, img_id_out)

        ans.get_group_document.assert_called_once_with('current')
        ans.find_picture.assert_called_once_with(str(img_id_in))
        Image.open.assert_called_once_with(ans.build_picture_path(picture_name='whatever', snap_id=snap_id))
        MockImage.resize.assert_called_once_with((image_width, image_height), Image.BICUBIC) 
        ImageOps.colorize.assert_called_once_with(the_mock_image, 1.1, 2.2)
        MockImage.save.assert_called_once_with(pic_path_out)
        ans.save_picture_document.assert_called_once_with(test_img_dict_out)

#test scale image with no colorize
#test scale image with bilinear
#test scale image with antialias
#test_scale_image_with_invalid_image_id
#test edge_detect with invalid image_id
#test edge_detect with a valid alternate_image_id
#test edge_detect with just a auto_id, no wide or tight
