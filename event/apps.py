from anthill.platform.apps import BaseAnthillApplication
import logging

logger = logging.getLogger('anthill.application')


class AnthillApplication(BaseAnthillApplication):
    """Anthill default application."""

    extra_models_modules = (
        'anthill.platform.core.celery.beatsqlalchemy.models',
    )
