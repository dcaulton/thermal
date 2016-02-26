import json
import uuid

from flask import Blueprint, request, Response, url_for
from merging.services import merge_images_task
from thermal.utils import get_url_base, item_exists

merging = Blueprint('merging', __name__)


@merging.route('/')
def index():
    url_base = get_url_base()
    top_level_links = {
        'merge_images': url_base + url_for('merging.call_merge_images'),
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')


# TODO add testing
@merging.route('/merge_images')
def call_merge_images():
    img1_id, img2_id = None, None
    if 'img1_id' in request.args:
        img1_id = request.args.get('img1_id')
    if 'img2_id' in request.args:
        img2_id = request.args.get('img2_id')

    if not item_exists(img1_id, 'picture'):  # TODO add testing for no picture id and invalid picture id
        err_msg = 'Source image 1 not found.  A valid id for a source image must be supplied to this endpoint as a get parameter'\
                  ' named img1_id in order to call this endpoint'
        return Response(json.dumps(err_msg), status=404, mimetype='application/json')

    if not item_exists(img2_id, 'picture'):  # TODO add testing for no picture id and invalid picture id
        err_msg = 'Source image 2 not found.  A valid id for a source image must be supplied to this endpoint as a get parameter'\
                  ' named img2_id in order to call this endpoint'
        return Response(json.dumps(err_msg), status=404, mimetype='application/json')

    result_id = uuid.uuid4()

    merge_images_task.delay(
        img1_primary_id_in=img1_id,
        img1_alternate_id_in=uuid.uuid4(),
        img2_id_in=img2_id,
        img_id_out=result_id,
        group_id='current'
    )
    accept_json = {'result_id': result_id}
    return Response(json.dumps(accept_json), status=202, mimetype='application/json')
