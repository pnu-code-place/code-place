"""
WSGI config for qduoj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from utils.observability_tracing import configure_opentelemetry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oj.settings")
configure_opentelemetry("codeplace-backend")

application = get_wsgi_application()
