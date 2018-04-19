from anthill.framework.utils.version import get_version

VERSION = (0, 0, 1, 'alpha', 1)

__version__ = get_version(VERSION)


def setup():
    """
    Configure the settings (this happens as a side effect of accessing the
    first setting) and configure logging.
    """
    from anthill.framework.conf import settings
    from anthill.framework.utils.log import configure_logging

    configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
