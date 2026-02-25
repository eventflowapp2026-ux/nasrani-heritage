#!/usr/bin/env bash
set -o errexit

export PYTHON_VERSION=3.11.9
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser from environment variables
python community/ensure_superuser.py

python --version
