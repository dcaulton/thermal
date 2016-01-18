# thermal
This is an application to let a Raspberry Pi use a pair of cameras to capture and post process thermal and regular visual camera information into new, blended images.  

A range of options are available to transform and merge these images into new pictures.


#Summary 
- This respository is for controlling a Raspberry Pi computer running the standard camera that comes with the Pi and a second thermal imaging camera
- Images are taken with both cameras and combined via ImageMagick.  In almost all cases that is done with its python PIL bindings.
- Python is the base language in preference for anything that can't happen with system packages and command line.
- This is run as a Flask application and all interaction is done with JSON and through RESTful APIs.
- CouchDB is the database.
- Interactions with the hardware are processed asynchronously by means of Celery.
- RabbitMQ is used as the message brokering service for Celery.
- A button on the project box can be used to trigger the camera.
- Galleries are supported by means of the API.
- Pictures can be uploaded to Amazon S3 for use with a gallery.
- Images can be automatically emailed.
- Colorization and all forms of image blending and merging are configurable, often at runtime.

#Hardware Requirements
It has been developed against the following system:
- Raspberry Pi 2 B computer, 32GB SD card
- Raspian Jessie OS (11.21.2015)
- Raspberry Pi standard camera
- FLIR Lepton camera with the Pure Engineering breakout board
- A project box with a momentary button and both cameras front mounted

#Installation Instructions
We will start with the following assumptions:
- The hostname for this Raspberry Pi will be strangefruit4.
- I'll be installing software and running it as the default pi user.

#prepare the memory card and perform the initial bootup on the RPi
- install the 11.21.15 version of Raspian Jessie (for RPi 2 B) on a 32GB micro SD card using Pi Filler on a Mac Mini.
- put the card in the Raspberry Pi 2 B, connect the RPi to power and ethernet.  
- after the pi has booted up:
  - ssh pi@raspberrypi # You are now connected to the machine
- sudo echo 'strangefruit4' > /etc/hostname
- if you have a USB wifi dongle plugged in to the unit, this is a good time to enter your credentials:
    sudo vi /etc/wpa_supplicant/wpa_supplicant.conf , add this to the bottom:
    network = {
      ssid="YOUR_WIFI_ACCESS_POINT_NAME",
      psk="YOUR_WIFI_PASSWORD",
      proto=RSN,
      key_mgmt=WPA-PSK,
      pairwise=TKIP,
      auth_alg=OPEN
    }
- sudo apt-get install vim
- sudo vim /etc/apt/sources.list , uncomment the line at the bottom
- sudo raspi-config
  - Enable Camera
  - Advanced Options > SPI > Enable Spi Module, also enable the SPI kernel module to load by default
  - Internationalization Options > set up your locale and timezone
  - Change User Password
  - Expand Filesystem
  - Finish
  - reboot the machine

##install Linux packages
- ssh pi@strangefruit4
- sudo apt-get update
- sudo apt-get upgrade
- set up the authorized key for my main linux desktop on strangefruit4
- sudo easy_install virtualenv
- sudo apt-get install python-dev python-opencv
- sudo apt-get install couchdb rabbitmq-server
- sudo apt-get build-dep python-imaging
- sudo apt-get install libjpeg9-dev
- sudo apt-get install imagemagick

##install python packages
- cd ~
- git clone https://github.com/dcaulton/thermal.git
- cd ~/thermal
- virtualenv venv
- source venv/bin/activate
- pip install numpy  ** I know, shouldn't be needed but it runs long with a lot of c compiles.  
- pip install -r requirements/common.txt
- git config --global user.email "dcaulton@gmail.com"; git config --global user.name "Dave Caulton"
- git config --global color.ui true
- touch ~/.vimrc; echo 'syntax on' > ~/.vimrc
- add this to ~/.bashrc:  
  - export EDITOR=/usr/bin/vim
  - export S3_ACCESS_KEY_ID = 'your_amazon_s3_access_key_id'
  - export S3_SECRET_ACCESS_KEY = 'your_secret_access_key'
  - export MAIL_USERNAME='your@email_address.com'
  - export MAIL_PASSWORD='your_email_password'

- ln -s /usr/lib/python2.7/dist-packages/cv2.arm-linux-gnueabihf.so ~/thermal/venv/lib/python2.7/site-packages/cv2.arm-linux-gnueabihf.so

##enable web admin interfaces for CouchDB and RabbitMQ
- Enable the CouchDB management panel access from other computers on the local network:
  - sudo vim /etc/couchdb/default.ini , update bind_address to 0.0.0.0.
  - maybe a sudo service couchdb restart?
  - *Now you can access the couchdb web interface from other computers/browsers on the local network at http://strangefruit4:5984/_utils*

- Enable the RabbitMQ management panel access from other points on the local network:
  - sudo rabbitmq-plugins enable rabbitmq_management
  - sudo rabbitmqctl add_user dave dave
  - sudo rabbitmqctl set_user_tags dave administrator 
  - sudo reboot  
  - *Now you can get at the rabbitmq admin server at http://strangefruit4:15672/#/  with the dave/dave credentials*

##enable listener for the button, celery, flask
- These tasks get the system up and listening for button and http inputs:
  - python /home/pi/thermal/run.py  **starts the Flask listener in dev mode
  - sh /home/pi/thermal/thermal/bin/start_celery_worker.sh  **starts the celery listener
  - sudo python /home/pi/thermal/thermal/bin/button_listener.py  **starts the button listener

At this point the system should be able to service api calls and take pictures.  Databases will be created and default group configuration files are created on first start and url access of the Flask application.

