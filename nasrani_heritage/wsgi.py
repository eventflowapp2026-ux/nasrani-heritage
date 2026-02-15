"""
WSGI config for nasrani_heritage project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nasrani_heritage.settings')

application = get_wsgi_application()  # This line is crucial!
