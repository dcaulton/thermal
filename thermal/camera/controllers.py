from flask import Blueprint


camera = Blueprint('camera', __name__)


@camera.route('/')
def index():
    return "Camera"

@camera.route('/thermal_still')
def thermal_still():
    print 'taking a thermal still'

