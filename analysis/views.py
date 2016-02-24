import json
import uuid

from flask import Blueprint, request, Response

from analysis.services import edge_detect_task, scale_image_task
from picture.services import find_picture
from thermal.utils import get_url_base

analysis = Blueprint('analysis', __name__)


@analysis.route('/')
def index():
    url_base = get_url_base()
    top_level_links = { 
        'scale_image': url_base + 'analysis/scale_image',
        'edge_detect': url_base + 'analysis/edge_detect',
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')


@analysis.route('/scale_image/<image_id>')
def call_scale_image():
    # TODO handle the case with no image_id gracefully, do the same in other endpoints here and in merging
    #  I think that means find_picture should 404 if it doesn't find anything, right now it just throws NotFoundError
    #  This probably means we should have try/except logic for all our view endpoints where we hit the db at all
    result_id = uuid.uuid4()
    find_picture(image_id)
    scale_image_task.delay(img_id_in=image_id, img_id_out=result_id, group_id='current')
    resp_json = {
        'scale_image_output_image_id': str(result_id)
    }
    return Response(json.dumps(resp_json), status=202, mimetype='application/json')


@analysis.route('/edge_detect/<image_id>')
def call_edge_detect(image_id):
    find_picture(image_id)
    auto_id = uuid.uuid4()
    wide_id = uuid.uuid4()
    tight_id = uuid.uuid4()
    edge_detect_task.delay(img_id_in=image_id, alternate_img_id_in=uuid.uuid4(), auto_id=auto_id, wide_id=wide_id,
                           tight_id=tight_id)
    resp_json = {
        'auto_id': str(auto_id),
        'wide_id': str(wide_id),
        'tight_id': str(tight_id)
    }
    return Response(json.dumps(resp_json), status=202, mimetype='application/json')
