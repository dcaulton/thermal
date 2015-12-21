from flask import Blueprint


camera = Blueprint('camera', __name__)


@camera.route('/')
def index():
    return "Camera"
