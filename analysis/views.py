import json

from flask import Blueprint, request, Response
from analysis.services import do_stuff, scale_image

analysis = Blueprint('analysis', __name__)

@analysis.route('/')
def do_analysis_stuff():
    things = do_stuff()
    return Response(json.dumps(things), status=200, mimetype='application/json')

@analysis.route('/scale_image')
def call_scale_image():
    (img_id_in, result_id) = (None, None)
    if request.args.has_key('img_id_in'):
        img_id_in = request.args.get('img_id_in')
    if request.args.has_key('result_id'):
        result_id = request.args.get('result_id')
    if img_id_in and result_id:
        scale_image(img_id_in=img_id_in, img_id_out=result_id)
        return Response(json.dumps('request accepted'), status=202, mimetype='application/json')
