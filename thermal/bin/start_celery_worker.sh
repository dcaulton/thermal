#! /bin/sh

#starts a celery worker to do the tasks 

export PATH=/home/pi/thermal/venv/bin:$PATH
cd /home/pi/thermal
celery -A thermal.celery worker --loglevel=info
