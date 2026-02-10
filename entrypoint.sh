#!/bin/sh
set -e

echo "Apply database migrations"
python manage.py migrate --noinput

echo "Collect static files"
echo "Ensure staticfiles directory exists and set ownership"
mkdir -p /app/staticfiles
# Try to set ownership to the runtime `appuser`; if the container isn't running as root
# this will fail and we silently continue (the collectstatic step will still run).
chown -R appuser:appuser /app/staticfiles 2>/dev/null || echo "chown skipped (not privileged)"
chmod -R u+rw /app/staticfiles 2>/dev/null || true

python manage.py collectstatic --noinput --clear

# run the given CMD
exec "$@"
