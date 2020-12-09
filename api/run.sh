#!/bin/bash
nohup python manage.py qcluster &
exec gunicorn --timeout 60 --bind :7000 --workers 3 api.wsgi:application