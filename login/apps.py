from anthill.platform.apps import BaseAnthillApplication
import logging

logger = logging.getLogger('anthill.application')


class AnthillApplication(BaseAnthillApplication):
    """Anthill default application."""

    def setup_extra_models(self):
        from anthill.framework.auth.social import models
        models.init_social()
