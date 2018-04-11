from celery import Celery
from anthill.framework.conf import settings

SETTINGS = getattr(settings, 'CELERY_SETTINGS', {})
APP_NAME = getattr(settings, 'CELERY_APP_NAME', 'tasks')

celery = Celery(APP_NAME)
celery.conf.update(SETTINGS)
