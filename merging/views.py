import json
import uuid

from flask import Blueprint, request, Response
from merging.services import merge_images_task

merging = Blueprint('merging', __name__)


@merging.route('/merge_images')
def call_merge_images():
    (img1_id, img2_id, result_id) = (None, None, None)
    if 'img1_id' in request.args:
        img1_id = request.args.get('img1_id')
    if 'img2_id' in request.args:
        img2_id = request.args.get('img2_id')
    if 'result_id' in request.args:
        result_id = request.args.get('result_id')
    if img1_id and img2_id and result_id:
        merge_images_task.delay(
            img1_primary_id_in=img1_id,
            img1_alternate_id_in=uuid.uuid4(),
            img2_id_in=img2_id,
            img_id_out=result_id,
            group_id='current'
        )
        return Response(json.dumps('request accepted'), status=202, mimetype='application/json')
