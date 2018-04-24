from celery import Celery
from anthill.framework.conf import settings
from anthill.common.core.celery.worker import start_worker
import logging

logger = logging.getLogger('celery')

SETTINGS = getattr(settings, 'CELERY_SETTINGS', {})
APP_NAME = getattr(settings, 'CELERY_APP_NAME', 'tasks')
USE_CELERY = getattr(settings, 'USE_CELERY', False)
WORKER_LOG_LEVEL = getattr(settings, 'CELERY_LOG_LEVEL', 'info')

celery = Celery(APP_NAME)
celery.conf.update(SETTINGS)


class CeleryMixin:
    def start_celery(self):
        if USE_CELERY:
            logger.debug('Celery is ON')
            with start_worker(app=celery, loglevel=WORKER_LOG_LEVEL):
                pass
        else:
            logger.debug('Celery is OFF')
