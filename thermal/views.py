import json

from flask import Blueprint, request, Response, url_for

from thermal.utils import get_url_base


thermal = Blueprint('thermal', __name__)


@thermal.route('/')
def index():
    # TODO we want to return an index of top level links for the apps, so admin, camera, etc.
    #  Hardcode for now, but the right way is to probe the application context for these
    #  TODO determine hostname and protocol automatically too
    url_base = get_url_base()
    top_level_links = {
        'admin': url_base + url_for('admin.index'),
        'camera': url_base + url_for('camera.index'),
        'pictures': url_base + url_for('picture.list_pictures'),
        'merging': url_base + url_for('merging.index'),
        'analysis': url_base + url_for('analysis.index'),
        'docs': url_base + '/docs/_build/html',
    }
    return Response(json.dumps(top_level_links), status=200, mimetype='application/json')
