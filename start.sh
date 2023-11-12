#!/bin/sh
OPENAI_API_KEY=$(jq -r '.openai_apikey' config/config.json)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "OPENAI_API_KEY is not set"
    exit 1
fi
export OPENAI_API_KEY=$OPENAI_API_KEY


python3 manage.py migrate


uwsgi --module=backend.wsgi:application \
     --env DJANGO_SETTINGS_MODULE=backend.settings \
     --master \
     --http=0.0.0.0:80 \
     --processes=5 \
     --harakiri=20 \
     --max-requests=5000 \
     --vacuum
