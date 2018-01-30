from microservices_framework.apps.cls import Application
from celery import Celery


class BaseAnthillApplication(Application):
    celery = Celery('anthill')
    celery.config_from_object('anthill_platform.celeryconfig')
