from anthill.platform.apps import BaseAnthillApplication
import logging

logger = logging.getLogger('anthill.application')


class AnthillApplication(BaseAnthillApplication):
    """Anthill default application."""

    models_modules = (
        'anthill.framework.auth.backends.db.models',
    )

    def get_models_modules(self):
        return super().get_models_modules() + self.models_modules

    def post_setup_models(self):
        from anthill.framework.auth.social import models
        models.init_social()
