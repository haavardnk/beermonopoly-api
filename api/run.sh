#!/bin/bash
nohup uv run manage.py qcluster &
uv run gunicorn --limit-request-line 8000 --timeout 60 --bind :7000 --workers 5 api.wsgi:application
