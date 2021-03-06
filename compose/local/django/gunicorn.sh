#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

python manage.py collectstatic --noinput
python /app/manage.py migrate
gunicorn haiyi.wsgi -w 1 -b 0.0.0.0:8000 --chdir=/app
