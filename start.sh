#!/bin/sh
sh config/config.sh

python3 manage.py migrate


uwsgi --module=backend.wsgi:application \
     --env DJANGO_SETTINGS_MODULE=backend.settings \
     --master \
     --http=0.0.0.0:80 \
     --processes=5 \
     --harakiri=20 \
     --max-requests=5000 \
     --vacuum
