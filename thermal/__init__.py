import socket

import couchdb
from flask import (g, Flask)

from camera.controller import camera
from admin.controller import admin
from picture.controller import picture
from crap.controller import crap

app = Flask(__name__)
app.config.from_object('thermal.config')
app.register_blueprint(camera, url_prefix='/camera')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(picture, url_prefix='/pictures')
app.register_blueprint(crap, url_prefix='/crap')

app.config['HOSTNAME'] = socket.gethostname()

@app.before_request
def before_request():
    couch = couchdb.Server()
    db = couch['thermal']
    g.db = db
