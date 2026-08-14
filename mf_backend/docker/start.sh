#!/bin/bash

cd /app

# if [ $# -eq 0 ]; then
#     echo "Usage: start.sh [PROCESS_TYPE](server/beat/worker/flower)"
#     exit 1
# fi

PROCESS_TYPE=$1

if [ "$DJANGO_DEBUG" = "true" ]; then
    echo "DJANGO_DEBUG = true"
    gunicorn \
        --reload \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --worker-class gevent \
        --log-level DEBUG \
        --access-logfile "gunicorn_logs/debug_access.log" \
        --error-logfile "gunicorn_logs/debug_error.log" \
        radian_backend.wsgi
else
    echo "DJANGO_DEBUG = false"
    gunicorn \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --worker-class gevent \
        --log-level DEBUG \
        --access-logfile "gunicorn_logs/access.log" \
        --error-logfile "gunicorn_logs/error.log" \
        radian_backend.wsgi
fi