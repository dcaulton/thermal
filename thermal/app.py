import datetime

import cv2
from flask import (g, Flask, request, Response)
import couchdb
import json
import numpy as np
import os
import picamera
from pylepton import Lepton
import sys
import uuid

app = Flask(__name__)
app.config.from_object('config')

current_group_id = uuid.uuid4()

@app.before_request
def before_request():
    couch=couchdb.Server()
    db = couch['thermal']
    g.db = couch['thermal']

def get_settings_document():
    map_fun = '''function(doc) {
        if (doc.type == 'settings')
            emit(doc._id, doc);
    }'''
    settings_dict = g.db.query(map_fun).rows[0]['value']
    return settings_dict
    
def find_pictures():
    pictures_dict = {}
    map_fun = '''function(doc) {
        if (doc.type == 'picture')
            emit(doc._id, doc);
    }'''
    for row in g.db.query(map_fun).rows:
        pictures_dict[row['key']] = row['value']
    return pictures_dict
    
@app.route('/')
def index():
    return 'Thermal App'

@app.route('/settings', methods=['GET'])
def get_settings():
    settings = get_settings_document()
    return Response(json.dumps(settings), status=200, mimetype='application/json')
    
@app.route('/settings', methods=['POST'])
def set_settings():
    settings = get_settings_document()
    if request.headers['Content-Type'] == 'application/json':
        print request.json
        for k in request.json.keys():
            if k != '_id':
                settings[k] = request.json[k]
        g.db[settings['_id']] = settings
        return Response(json.dumps(settings), status=200, mimetype='application/json')

@app.route('/picam_still')
def picam_still():
    with picamera.PiCamera() as camera:
        datetime_str = str(datetime.datetime.today())
        pic_path = os.path.join('/home/pi', 'Pictures', datetime_str+'-picam_pic.jpg')
        camera.capture(pic_path)
        pic_id = str(uuid.uuid4())
        pic_dict = {'type': 'picture',
                    'camera_type': 'picam',
                    'group_id': str(current_group_id),
                    'uri': 'file://strangefruit4'+pic_path,
                    'created': str(datetime.datetime.now())
                   }
        g.db[pic_id] = pic_dict
        return Response(json.dumps(pic_dict), status=200, mimetype='application/json')

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
            pic_id = str(uuid.uuid4())
            pic_dict = {'type': 'picture',
                        'camera_type': 'thermal',
                        'group_id': str(current_group_id),
                        'uri': 'file://strangefruit4'+pic_path,
                        'created': str(datetime.datetime.now())
                       }
            g.db[pic_id] = pic_dict
            return Response(json.dumps(pic_dict), status=200, mimetype='application/json')
    except Exception as e:
        e = sys.exc_info()[0]
        return Response(json.dumps(e), status=404, mimetype='application/json')

@app.route('/pictures')
def pictures():
    pictures = find_pictures()
    return Response(json.dumps(pictures), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.debug = True
    app.run(host='strangefruit4', port=5000)
