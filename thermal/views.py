import json

from flask import Blueprint, request, Response, url_for

from thermal.utils import get_url_base


thermal = Blueprint('thermal', __name__)


@thermal.route('/')
def index():
    url_base = get_url_base()
    top_level_links = {
        'admin': url_base + url_for('admin.index'),
        'camera': url_base + url_for('camera.index'),
        'pictures': url_base + url_for('picture.list_pictures'),
        'merging': url_base + url_for('merging.index'),
        'analysis': url_base + url_for('analysis.index'),
        'calibration': url_base + url_for('calibration.index'),
        'docs': url_base + '/docs/_build/html',
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')
