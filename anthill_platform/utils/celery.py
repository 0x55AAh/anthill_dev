from celery import Celery
from microservices_framework.conf import settings

CELERY_SETTINGS = getattr(settings, 'CELERY', {})

celery = Celery('anthill')
celery.conf.update(CELERY_SETTINGS)
