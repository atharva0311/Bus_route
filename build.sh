#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Clear cached bytecode to prevent stale .pyc files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

python manage.py collectstatic --noinput
python manage.py migrate
