#!/bin/sh
set -e
alembic -c /app/src/app/backend/alembic.ini upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
exec nginx -g 'daemon off;'
