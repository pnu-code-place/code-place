"""
WSGI config for csep_scheduler project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.utils.module_loading import import_string

from csep_scheduler import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csep_scheduler.settings')

application = get_wsgi_application()
try:
    scheduler_class = import_string(settings.SCHEDULER_CLASS)
    scheduler = scheduler_class()
    scheduler.start()
except AttributeError:
    pass
