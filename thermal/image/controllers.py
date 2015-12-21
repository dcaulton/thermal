from flask import Blueprint


image = Blueprint('image', __name__)


@image.route('/')
def index():
    return "Image"
