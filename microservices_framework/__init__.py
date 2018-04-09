from microservices_framework.utils.version import get_version

VERSION = (0, 0, 1, 'alpha', 1)

__version__ = get_version(VERSION)


def setup():
    from microservices_framework.conf import settings
    from microservices_framework.utils.log import configure_logging

    configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
