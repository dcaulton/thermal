import couchdb
from flask import (g, Flask)

from thermal.camera.controller import camera
from thermal.admin.controller import admin
from thermal.picture.controller import picture

app = Flask(__name__)
app.config.from_object('thermal.config')
app.register_blueprint(camera, url_prefix='/camera')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(picture, url_prefix='/pictures')

@app.before_request
def before_request():
    couch = couchdb.Server()
    db = couch['thermal']
    g.db = couch['thermal']
