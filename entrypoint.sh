#!/bin/sh
set -e

echo "Apply database migrations"
python manage.py migrate --noinput

echo "Collect static files"
python manage.py collectstatic --noinput --clear

# run the given CMD
exec "$@"
