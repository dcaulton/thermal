import datetime

from flask import Flask
import picamera
import os


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello World'

@app.route('/picam_still')
def picam_still():
    with picamera.PiCamera() as camera:
        datetime_str = str(datetime.datetime.today())
        pic_path = os.path.join('/home/pi', 'Pictures', datetime_str+'-picam_pic.jpg')
        camera.capture(pic_path)
        return pic_path


if __name__ == '__main__':
    app.run()
