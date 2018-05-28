from celery import Celery
from anthill.framework.conf import settings
from anthill.platform.core.celery.worker import start_worker
import logging

logger = logging.getLogger('celery')

SETTINGS = getattr(settings, 'CELERY_SETTINGS', {})
CELERY_ENABLE = getattr(settings, 'CELERY_ENABLE', False)
TIME_ZONE = getattr(settings, 'TIME_ZONE', 'UTC')

celery_app = Celery()
celery_app.conf.update(SETTINGS)


class CeleryMixin:
    @staticmethod
    def start_celery():
        if CELERY_ENABLE:
            logger.debug('Celery is enabled.')
            with start_worker(app=celery_app, timezone=TIME_ZONE):
                pass
        else:
            logger.debug('Celery is disabled.')
