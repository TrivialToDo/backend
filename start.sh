#!/bin/sh
sh config/config.sh

python3 manage.py migrate


uwsgi --module=backend.wsgi:application \
     --env DJANGO_SETTINGS_MODULE=backend.settings \
     --master \
     --http=0.0.0.0:80 \
     --processes=4 \
     --harakiri=60 \
     --max-requests=5000 \
     --enable-threads \
     --mule=backend/apscheduler_start.py \
     --vacuum
