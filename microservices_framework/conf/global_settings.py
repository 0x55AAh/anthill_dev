"""
Default service settings. Override these with settings in the module pointed to
by the SERVICE_SETTINGS_MODULE environment variable.
"""

####################
# CORE             #
####################

SECRET_KEY = None

DEBUG = False

DATABASES = None

RESOLVERS = None

TIME_ZONE = 'UTC'

LOCATION = 'http://127.0.0.1:9500'

ROUTES_CONF = None

APPLICATION_CLASS = None
APPLICATION_NAME = None
APPLICATION_VERBOSE_NAME = None
APPLICATION_DESCRIPTION = None
APPLICATION_ICON_CLASS = None

SERVICE_CLASS = None

###########
# LOGGING #
###########

# The callable to use to configure logging
LOGGING_CONFIG = 'logging.config.dictConfig'

# Custom logging configuration.
LOGGING = {}
