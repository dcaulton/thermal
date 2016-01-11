from flask import Blueprint, request, Response
import json

from admin.services import default_group_dict, get_settings_document, get_group_document, save_document
from thermal.exceptions import NotFoundError

#from thermal.appmodule import mail
#from flask import current_app
#from flask.ext.mail import Message

admin = Blueprint('admin', __name__)

#add a test on the service side to check the integrity of settings.current_group_id on settings save.
#  we don't need to worry about deletes, just updates
@admin.route('/')
def index():
    return 'Admin'

#@admin.route('/send_email', methods=['GET'])
#def send_email():
#    image_path = '/home/pi/smalls.jpg'
#    subject = 'poop subject'
#    sender = 'jackweed@sturgis.com'
#    recipients = ['dcaulton@gmail.com']
#    text_body = 'some text body'
#    html_body = '<html><body><bold>THIS</bold> is an email</body></html>'
#    msg = Message(subject, sender=sender, recipients=recipients)
#    msg.body = text_body
#    msg.html = html_body
#    with current_app.open_resource(image_path) as fp:
#        msg.attach(image_path, "image/jpeg", fp.read())
#    mail.send(msg)
#    return Response(json.dumps('mail sent'), status=200, mimetype='application/json')
#    
@admin.route('/settings', methods=['GET'])
def get_settings():
    settings = get_settings_document()
    return Response(json.dumps(settings), status=200, mimetype='application/json')
    
@admin.route('/settings', methods=['PUT'])
def update_settings():
    settings = get_settings_document()
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if doc_attribute_can_be_set(k):
                settings[k] = request.json[k]
        save_document(settings)
        return Response(json.dumps(settings), status=200, mimetype='application/json')

@admin.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    try:
        group_dict = get_group_document(group_id)
    except NotFoundError as e:
        return Response(json.dumps(e.message), status=e.status_code, mimetype='application/json')
    return Response(json.dumps(group_dict), status=200, mimetype='application/json')

@admin.route('/groups/<group_id>', methods=['PUT'])
def update_group(group_id):
    group_dict = get_group_document(group_id)
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if doc_attribute_can_be_set(k):
                group_dict[k] = request.json[k]
        save_document(group_dict)
        return Response(json.dumps(group_dict), status=200, mimetype='application/json')

@admin.route('/groups', methods=['POST'])
def save_group():
    settings = get_settings_document()
    group_dict = default_group_dict()
    if request.headers['Content-Type'] == 'application/json':
        for k in request.json.keys():
            if doc_attribute_can_be_set(k):
                group_dict[k] = request.json[k]
        save_document(group_dict)
        settings['current_group_id'] = group_dict['_id']
        save_document(settings)
        return Response(json.dumps(group_dict), status=200, mimetype='application/json')

def doc_attribute_can_be_set(key_name):
    if key_name not in ['_id', '_rev']:
        return True
    return False
