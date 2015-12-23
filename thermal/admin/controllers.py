from flask import Blueprint


admin = Blueprint('admin', __name__)


@admin.route('/')
def index():
    return "Admin"

@admin.route('/show_status')
def index():
    return "current status:"
