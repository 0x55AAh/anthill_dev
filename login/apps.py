from anthill.platform.apps import BaseAnthillApplication
import logging

logger = logging.getLogger('anthill.application')


class AnthillApplication(BaseAnthillApplication):
    """Anthill default application."""

    extra_models_modules = (
        'anthill.framework.auth.backends.db.models',
    )

    def post_setup_models(self):
        from anthill.framework.auth.social import models
        models.init_social()
