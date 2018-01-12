from microservices_framework.utils.version import get_version

VERSION = (0, 1, 0, 'alpha', 0)

__version__ = get_version(VERSION)


def setup():
    from microservices_framework.conf import settings
    from microservices_framework.utils.log import configure_logging

    configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
