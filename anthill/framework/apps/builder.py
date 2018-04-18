from anthill.framework.utils.module_loading import import_string
from anthill.framework.conf import settings
from .cls import Application
import logging

logger = logging.getLogger('app')


class AppBuilder:
    default_application_class = Application

    def get_class(self):
        application_class = self.default_application_class
        if settings.APPLICATION_CLASS is not None:
            try:
                application_class = import_string(settings.APPLICATION_CLASS)
            except ImportError as e:
                logger.warning(str(e))
                logger.warning(
                    'Cannot import application class: %s. Default used.' % settings.APPLICATION_CLASS)
        return application_class

    def build(self):
        application_class = self.get_class()
        instance = application_class()
        logger.info('Application \'%s\' loaded.' % instance.name)
        return instance


app = AppBuilder().build()
app.setup()
