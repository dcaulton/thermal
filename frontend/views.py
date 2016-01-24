from flask import Blueprint, request, render_template

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
@frontend.route('/index')
def frontend_home():
    user = {'nickname': 'Bocephus'}  # fake user
    return render_template('index.html',
                           title='Home',
                           user=user)
