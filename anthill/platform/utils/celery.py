from celery import Celery
from anthill.framework.conf import settings
from anthill.platform.core.celery.worker import start_worker
import logging

logger = logging.getLogger('celery')

SETTINGS = getattr(settings, 'CELERY_SETTINGS', {})
CELERY_ENABLE = getattr(settings, 'CELERY_ENABLE', False)
WORKER_LOG_LEVEL = getattr(settings, 'CELERY_LOG_LEVEL', 'info')

celery = Celery()
celery.conf.update(SETTINGS)


class CeleryMixin:
    def start_celery(self):
        if CELERY_ENABLE:
            logger.debug('Celery is enabled.')
            with start_worker(
                    app=celery,
                    concurrency=1,
                    loglevel=WORKER_LOG_LEVEL):
                pass
        else:
            logger.debug('Celery is disabled.')
