from celery import Celery
from anthill.framework.conf import settings
from anthill.platform.core.celery.worker import start_worker

__all__ = ['app', 'start_worker']

SETTINGS = getattr(settings, 'CELERY_SETTINGS', {})


app = Celery()
app.conf.update(SETTINGS)
