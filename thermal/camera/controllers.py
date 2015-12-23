from flask import Blueprint


camera = Blueprint('camera', __name__)


@camera.route('/')
def index():
    return "Camera"

@camera.route('/thermal_still')
def capture_image():
    print 'taking a thermal still'

