from anthill.framework.apps.cls import Application
from anthill.platform.api.internal import api as internal_api
from anthill.framework.conf import settings
from importlib import import_module
import logging


logger = logging.getLogger('anthill.application')


class BaseAnthillApplication(Application):
    """Base anthill application."""

    def __init__(self):
        super().__init__()
        self.internal = internal_api

    def get_models_modules(self):
        models_modules = super().get_models_modules()
        return models_modules

    # noinspection PyMethodMayBeStatic
    def get_internal_api_modules(self):
        api_modules = (
            settings.INTERNAL_API_CONF,
        )
        return api_modules

    def setup_internal_api(self):
        logger.debug('Internal api installing...')
        internal_api.service = self.service
        for api_module in self.get_internal_api_modules():
            import_module(api_module)
        logger.debug('\_ Internal api methods: %s' % ', '.join(internal_api.methods))
        logger.debug('\_ Internal api installed.')

    def post_setup(self):
        self.setup_internal_api()
