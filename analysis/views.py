import json
import uuid

from flask import Blueprint, request, Response, url_for

import analysis.services as ans
from thermal.utils import get_document_with_exception, get_url_base, item_exists

analysis = Blueprint('analysis', __name__)


@analysis.route('/')
def index():
    '''
    Lists top level endpoints for analysis
    '''
    url_base = get_url_base()
    top_level_links = { 
        'scale_image': url_base + url_for('analysis.call_scale_image'),
        'edge_detect': url_base + url_for('analysis.call_edge_detect'),
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')


@analysis.route('/scale_image')
@analysis.route('/scale_image/<image_id>')
def call_scale_image(image_id=None):
    '''
    Scales an image according to the current group settings
    '''
    result_id = uuid.uuid4()

    if not item_exists(image_id, 'picture'):  # TODO add testing for no picture id and invalid picture id
        err_msg = 'Image not found.  A valid image_id must be supplied as the last segment of the url in order to call'\
                  ' this endpoint'
        return Response(json.dumps(err_msg), status=404, mimetype='application/json')
    else:
        get_document_with_exception(image_id, 'picture')
        ans.scale_image_task.delay(img_id_in=image_id, img_id_out=result_id, group_id='current')
        resp_json = {
            'scale_image_output_image_id': str(result_id)
        }
        return Response(json.dumps(resp_json), status=202, mimetype='application/json')


@analysis.route('/edge_detect')
@analysis.route('/edge_detect/<image_id>')
def call_edge_detect(image_id=None):
    '''
    Invokes edge detection for a given image
    '''
    if not item_exists(image_id, 'picture'):  # TODO add testing for no picture id and invalid picture id
        err_msg = 'Image not found.  A valid image_id must be supplied as the last segment of the url in order to call'\
                  ' this endpoint'
        return Response(json.dumps(err_msg), status=404, mimetype='application/json')
    else:
        get_document_with_exception(image_id, 'picture')
        auto_id = uuid.uuid4()
        wide_id = uuid.uuid4()
        tight_id = uuid.uuid4()
        ans.edge_detect_task.delay(img_id_in=image_id, alternate_img_id_in=uuid.uuid4(), auto_id=auto_id, wide_id=wide_id,
                               tight_id=tight_id)
        resp_json = {
            'auto_id': str(auto_id),
            'wide_id': str(wide_id),
            'tight_id': str(tight_id)
        }
        return Response(json.dumps(resp_json), status=202, mimetype='application/json')
