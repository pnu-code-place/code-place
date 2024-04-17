"""
WSGI config for qduoj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oj.settings")

application = get_wsgi_application()

from django.utils.module_loading import import_string
from django.conf import settings

try:
    scheduler_class = import_string(settings.SCHEDULER_CLASS)
    scheduler = scheduler_class()
    scheduler.start()
except AttributeError:
    pass
