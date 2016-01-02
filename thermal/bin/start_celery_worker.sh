#! /bin/sh

#starts a celery worker to do the tasks requested by the crap controller

export PATH=/home/pi/thermal/venv/bin:$PATH
cd /home/pi/thermal
celery -A thermal worker --loglevel=info
