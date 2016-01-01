#!/home/pi/thermal/venv/bin/python

# Invoke with 'sudo python button_listener.py', sudo is needed for GPIO

# script by Alex Eames http://RasPi.tv/
# http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio
import os
import sys

#hack until I figure out why the virtualenv-modified sys.path isn't working
sys.path.append('/home/pi/thermal/venv/local/lib/python2.7/site-packages')

import RPi.GPIO as GPIO
import couchdb

capture_type='both_still'
button_active = False

def get_settings_document():
    global capture_type  #not elegant, clean up soon
    global button_active

    couch = couchdb.Server()
    db = couch['thermal']

    map_fun = '''function(doc) {
        if (doc.type == 'settings')
            emit(doc._id, doc);
    }'''
    view_result = db.query(map_fun)
    if view_result.total_rows:
        settings_dict = view_result.rows[0]['value']
    if 'capture_type' in settings_dict:
        capture_type = settings_dict['capture_type']
    if 'button_active' in settings_dict:
        button_active = settings_dict['button_active']

def initialize_gpio():
    GPIO.setmode(GPIO.BCM)

    # GPIO 18 set up as input. It is pulled up to stop false signals
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # now the program will do nothing until the signal on port 18 
    # starts to fall towards zero. This is why we used the pullup
    # to keep the signal high and prevent a false interrupt


initialize_gpio()

try:
    while True:
        GPIO.wait_for_edge(18, GPIO.FALLING)
        get_settings_document()
        if button_active:
            os.system("curl 'http://127.0.0.1:5000/camera/{0}'".format(capture_type))
except Exception as e:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
