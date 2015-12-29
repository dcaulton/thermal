import datetime

import cv2
from flask import (g, Flask)
from flaskext import couchdb
import numpy as np
import os
import picamera
from pylepton import Lepton
import sys
import uuid

app = Flask(__name__)
app.config.from_object('config')


@app.route('/')
def hello():
    return 'Thermal App'

@app.route('/settings', methods=['GET'])
def get_settings():
    try:
        manager = couchdb.CouchDBManager()
        manager.setup(app)
        import pdb; pdb.set_trace()
        settings = {'looking': 'good'}
        g.couch[uuid.uuid4()] = settings
    except Exception as e:
        settings = {'pooped the bed': str(e)}
    print settings
    return settings
    
@app.route('/settings', methods=['POST'])
def set_settings():
    try:
        manager = couchdb.CouchDBManager()
        manager.setup(app)
    except Exception as e:
        settings = {'pooped the bed': str(e)}
    print settings
    return settings

@app.route('/picam_still')
def picam_still():
    with picamera.PiCamera() as camera:
        datetime_str = str(datetime.datetime.today())
        pic_path = os.path.join('/home/pi', 'Pictures', datetime_str+'-picam_pic.jpg')
        camera.capture(pic_path)
        return pic_path

@app.route('/thermal_still')
def thermal_still():
    try:
        with Lepton("/dev/spidev0.1") as l:
            a,_ = l.capture()
            cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX) 
            np.right_shift(a, 8, a) 
            datetime_str = str(datetime.datetime.today())
            pic_path = os.path.join('/home/pi', 'Pictures', datetime_str+'-thermal_pic.jpg')
            cv2.imwrite(pic_path, np.uint8(a)) 
    except Exception as e:
        e = sys.exc_info()[0]
        print e
        return e

if __name__ == '__main__':
    app.run(host='strangefruit4', port=5000)
