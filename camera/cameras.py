import abc
from fractions import Fraction
from time import sleep

import cv2
import numpy as np
import picamera
import pylepton


class Camera(object):
    '''
    Base class to represent both the Picam ambient light camera and the Lepton, a thermal camera
    '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def take_still(self, pic_path):
        pass


class Picam(Camera):
    '''
    Handles taking pictures with with the Picam (ambient light) camera via the software bindings from the picamera package
    '''

    def __init__(self):
        pass

    def take_still(self, pic_path):
        self.take_normal_exposure_still(pic_path=pic_path, width=1200, height=900)

    def take_still(self, pic_path, image_width, image_height):
        self.take_normal_exposure_still(
            pic_path=pic_path,
            image_width=image_width,
            image_height=image_height
        )

    def take_normal_exposure_still(self, pic_path, image_width, image_height):
        with picamera.PiCamera() as camera:
            camera.resolution = (image_width, image_height)
            camera.capture(pic_path)

    def take_long_exposure_still(self, pic_path, image_width, image_height):
        with picamera.PiCamera() as camera:
            camera.resolution = (image_width, image_height)
            # Set a framerate of 1/6fps, then set shutter
            # speed to 6s and ISO to 800
            camera.framerate = Fraction(1, 6)
            camera.shutter_speed = 6000000
            camera.exposure_mode = 'off'
            camera.iso = 800
            # Give the camera a good long time to measure AWB
            # (you may wish to use fixed AWB instead)
            sleep(2)
            # Finally, capture an image with a 6s exposure. Due
            # to mode switching on the still port, this will take
            # longer than 6 seconds
            camera.capture(pic_path)


class Lepton(Camera):
    '''
    Handles taking pictures with the Lepton (thermal) camera using the software bindings in the pylepton package
    '''

    def __init__(self):
        pass

    def take_still(self, pic_path):
        # TODO push the spi specifics into config paramters
        with pylepton.Lepton("/dev/spidev0.1") as l:
            a, _ = l.capture()
            cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
            np.right_shift(a, 8, a)
            cv2.imwrite(pic_path, np.uint8(a))
