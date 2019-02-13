from anthill.framework.conf import settings
from anthill.platform.core.celery import start_worker, app as celery_app
import logging

logger = logging.getLogger('anthill.application')

CELERY_ENABLE = getattr(settings, 'CELERY_ENABLE', False)
TIME_ZONE = getattr(settings, 'TIME_ZONE', 'UTC')


class CeleryMixin:
    # noinspection PyMethodMayBeStatic
    def start_celery(self):
        if CELERY_ENABLE:
            logger.debug('Celery status: ENABLED.')
            with start_worker(app=celery_app, timezone=TIME_ZONE, loglevel=settings.DEBUG):
                pass
        else:
            logger.debug('Celery status: DISABLED.')
