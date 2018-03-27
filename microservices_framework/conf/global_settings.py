"""
Default service settings. Override these with settings in the module pointed to
by the SERVICE_SETTINGS_MODULE environment variable.
"""

########
# CORE #
########

SECRET_KEY = None

DEBUG = False

DATABASES = None

RESOLVERS = None

TIME_ZONE = 'UTC'
USE_TZ = False

LOCATION = 'http://localhost:9500'

ROUTES_CONF = None
MODELS_CONF = None
MANAGEMENT_CONF = None

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

# The email backend to use.
# The default is to use the SMTP backend.
# Third-party backends can be specified by providing a Python path
# to a module that defines an EmailBackend class.
EMAIL_BACKEND = 'microservices_framework.core.mail.backends.smtp.EmailBackend'

# Host for sending email.
EMAIL_HOST = 'localhost'

# Port for sending email.
EMAIL_PORT = 25

# Whether to send SMTP 'Date' header in the local time zone or in UTC.
EMAIL_USE_LOCALTIME = False

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = ''

# Default email address to use for various automated correspondence from
# the site managers.
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# Email address that error messages come from.
SERVER_EMAIL = 'root@localhost'

# Default file storage mechanism that holds media.
DEFAULT_FILE_STORAGE = 'microservices_framework.core.files.storage.FileSystemStorage'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# List of upload handler classes to be applied in order.
FILE_UPLOAD_HANDLERS = [
    'microservices_framework.core.files.uploadhandler.MemoryFileUploadHandler',
    'microservices_framework.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Maximum size, in bytes, of a request before it will be streamed to the
# file system instead of into memory.
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # i.e. 2.5 MB

# Directory in which upload streamed files will be temporarily saved. A value of
# `None` will make Django use the operating system's default temporary directory
# (i.e. "/tmp" on *nix systems).
FILE_UPLOAD_TEMP_DIR = None

# The numeric mode to set newly-uploaded files to. The value should be a mode
# you'd pass directly to os.chmod; see https://docs.python.org/3/library/os.html#files-and-directories.
FILE_UPLOAD_PERMISSIONS = None

# The numeric mode to assign to newly-created directories, when uploading files.
# The value should be a mode as you'd pass to os.chmod;
# see https://docs.python.org/3/library/os.html#files-and-directories.
FILE_UPLOAD_DIRECTORY_PERMISSIONS = None


#########
# CACHE #
#########

# The cache backends to use.
CACHES = {
    'default': {
        'BACKEND': 'microservices_framework.core.cache.backends.locmem.LocMemCache',
    }
}


# People who get code error notifications.
# In the format [('Full Name', 'email@example.com'), ('Full Name', 'anotheremail@example.com')]
ADMINS = []

# Not-necessarily-technical managers of the site. They get broken link
# notifications and other various emails.
MANAGERS = ADMINS

##############
# SQLALCHEMY #
##############

SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_BINDS = []
SQLALCHEMY_NATIVE_UNICODE = None
SQLALCHEMY_ECHO = False
SQLALCHEMY_RECORD_QUERIES = False

SQLALCHEMY_POOL_SIZE = None
SQLALCHEMY_POOL_TIMEOUT = None
SQLALCHEMY_POOL_RECYCLE = None
SQLALCHEMY_MAX_OVERFLOW = None

SQLALCHEMY_COMMIT_ON_TEARDOWN = False
SQLALCHEMY_TRACK_MODIFICATIONS = False


###########
# SIGNING #
###########

SIGNING_BACKEND = 'microservices_framework.core.signing.TimestampSigner'


##################
# AUTHENTICATION #
##################

AUTH_USER_MODEL = 'User'

# The first hasher in this list is the preferred algorithm.
# Any password using different algorithms will be converted automatically
# upon login
PASSWORD_HASHERS = [
    'microservices_framework.auth.hashers.PBKDF2PasswordHasher',
    'microservices_framework.auth.hashers.PBKDF2SHA1PasswordHasher',
    'microservices_framework.auth.hashers.Argon2PasswordHasher',
    'microservices_framework.auth.hashers.BCryptSHA256PasswordHasher',
    'microservices_framework.auth.hashers.BCryptPasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = []


##########
# CELERY #
##########

CELERY_LOG_LEVEL = 'error'

# All celery configuration options:
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#configuration
CELERY_SETTINGS = {
    'broker_url': 'amqp://guest:guest@localhost:5672',
    'result_backend': 'redis://'
}

CELERY_APP_NAME = 'tasks'


##########
# SERVER #
##########

STATIC_PATH = None
STATIC_URL = '/static/'

TEMPLATE_PATH = None

COMPRESS_RESPONSE = False

LOGIN_URL = None

UI_MODULE = None
