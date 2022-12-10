#!/bin/bash
nohup python manage.py qcluster &
exec gunicorn --limit-request-line 8000 --timeout 60 --bind :7000 --workers 3 api.wsgi:application