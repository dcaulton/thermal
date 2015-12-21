from flask import Flask
from thermal.admin.controllers import admin
from thermal.camera.controllers import camera
from thermal.image.controllers import image

app = Flask(__name__)

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(camera, url_prefix='/camera')
app.register_blueprint(image, url_prefix='/image')
