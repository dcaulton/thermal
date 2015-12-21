from celery import Celery
import os

app = Celery('tasks', broker='amqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y

#take thermal pic, move it to work dir
@app.task
def thermal_still():
    os.system("cd /home/pi/pictures; /home/pi/LeptonModule-master/software/raspberrypi_capture/raspberrypi_capture")

