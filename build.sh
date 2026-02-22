#!/usr/bin/env bash
# Exit on error
set -o errexit

# Force Python 3.11 (this is the key line that was missing!)
export PYTHON_VERSION=3.11.9

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Optional: Show Python version to verify
python --version
