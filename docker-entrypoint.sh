#!/bin/sh
# Update database
/app/.venv/bin/alembic upgrade head

exec "$@"