from anthill.framework.utils.translation import translate_lazy as _
from anthill.platform.conf.settings import *
from datetime import timedelta
import os

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+^a$ohe7j=fvitfyh__77m_24cc5zw1@9j9lhe@-*e)&amp;-m5zv3'

DEBUG = False

ADMINS = (
    ('Lysenko Vladimir', 'wofkin@gmail.com'),
)

SQLALCHEMY_DATABASE_URI = 'postgres://anthill_login@/anthill_login'

LOCATION = 'http://localhost:9607'
BROKER = 'amqp://guest:guest@localhost:5672'

# ROUTES_CONF = 'login.routes'

APPLICATION_CLASS = 'login.apps.AnthillApplication'
APPLICATION_NAME = 'login'
APPLICATION_VERBOSE_NAME = _('Login')
APPLICATION_DESCRIPTION = _('Manage user accounts, credentials and access tokens')
APPLICATION_ICON_CLASS = 'icon-key'
APPLICATION_COLOR = 'pink'

EMAIL_SUBJECT_PREFIX = '[Anthill: login] '

# SERVICE_CLASS = 'login.services.Service'

TEMPLATE_PATH = os.path.join(BASE_DIR, 'ui', 'templates')
LOCALE_PATH = os.path.join(BASE_DIR, 'locale')

CACHES["default"]["LOCATION"] = "redis://localhost:6379/17"
CACHES["default"]["KEY_PREFIX"] = "login.anthill"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'anthill.framework.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'anthill.framework.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'anthill.server': {
            '()': 'anthill.framework.utils.log.ServerFormatter',
            'fmt': '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'color': False,
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'anthill.server',
        },
        'anthill.server': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT_DIR, 'login.log'),
            'formatter': 'anthill.server',
            'maxBytes': 100 * 1024 * 1024,  # 100 MiB
            'backupCount': 10
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'anthill.framework.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'anthill': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'anthill.application': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'tornado.access': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'tornado.application': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'tornado.general': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'celery': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'celery.worker': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'celery.task': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'celery.redirected': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'asyncio': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

#########
# GEOIP #
#########

GEOIP_PATH = os.path.join(BASE_DIR, '../')

#########
# HTTPS #
#########

# HTTPS = {
#     'key_file': os.path.join(BASE_DIR, '../server.key'),
#     'crt_file': os.path.join(BASE_DIR, '../server.crt'),
# }
HTTPS = None

############
# GRAPHENE #
############

GRAPHENE = {
    'SCHEMA': 'login.api.v1.public.schema',
    'MIDDLEWARE': ()
}

##################
# AUTHENTICATION #
##################

AUTH_USER_MODEL = 'User'

AUTHENTICATION_BACKEND_MANAGER = {
    'AUTHORIZER_CLASS': 'anthill.framework.auth.backends.authorizer.DefaultAuthorizer',
    'DATASTORE_REALMS': [
        {
            'REALM_CLASS': 'anthill.framework.auth.backends.realm.DatastoreRealm',
            'DATASTORE_CLASS': 'anthill.framework.auth.backends.jwt.storage.JWTStore',
        },
    ]
}

AUTHENTICATION_BACKENDS = [
    # GOOGLE
    'anthill.framework.auth.social.backends.google.GoogleOAuth2',

    # FACEBOOK
    'anthill.framework.auth.social.backends.facebook.FacebookOAuth2',
    'anthill.framework.auth.social.backends.facebook.FacebookAppOAuth2',

    # VK
    'anthill.framework.auth.social.backends.vk.VKontakteOpenAPI',
    'anthill.framework.auth.social.backends.vk.VKAppOAuth2',
    'anthill.framework.auth.social.backends.vk.VKOAuth2',

    # MAILRU
    'anthill.framework.auth.social.backends.mailru.MailruOAuth2',

    # STEAM
    'anthill.framework.auth.social.backends.steam.SteamOpenId',

    # GITHUB
    'anthill.framework.auth.social.backends.github.GithubOAuth2',

    # DISCORD
    'anthill.framework.auth.social.backends.discord.DiscordOAuth2',

    # JWT
    'anthill.framework.auth.backends.JWTBackend',

    # LOGIN/PASSWORD
    'anthill.framework.auth.backends.ModelBackend'
]

JWT_AUTHENTICATION = {
    'JWT_ENCODE_HANDLER': 'anthill.framework.auth.token.jwt.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER': 'anthill.framework.auth.token.jwt.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER': 'anthill.framework.auth.token.jwt.utils.jwt_payload_handler',
    'JWT_PAYLOAD_GET_USER_ID_HANDLER': 'anthill.framework.auth.token.jwt.utils.jwt_get_user_id_from_payload_handler',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'anthill.framework.auth.token.jwt.utils.jwt_get_username_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'anthill.framework.auth.token.jwt.utils.jwt_response_payload_handler',

    'JWT_PRIVATE_KEY': None,
    'JWT_PUBLIC_KEY': None,

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': timedelta(seconds=300),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,
}

SOCIAL_AUTH_STRATEGY = 'anthill.framework.auth.social.strategy.TornadoStrategy'
SOCIAL_AUTH_STORAGE = 'anthill.framework.auth.social.models.TornadoStorage'

SOCIAL_AUTH_PIPELINE = [
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'anthill.framework.auth.social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'anthill.framework.auth.social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'anthill.framework.auth.social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'anthill.framework.auth.social.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'anthill.framework.auth.social.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # 'anthill.framework.auth.social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address.
    # 'anthill.framework.auth.social.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'anthill.framework.auth.social.pipeline.user.create_user',

    # Create the record that associated the social account with this user.
    'anthill.framework.auth.social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'anthill.framework.auth.social.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'anthill.framework.auth.social.pipeline.user.user_details'
]

SOCIAL_AUTH_DISCONNECT_PIPELINE = [
    # Verifies that the social association can be disconnected from the current
    # user (ensure that the user login mechanism is not compromised by this
    # disconnection).
    'anthill.framework.auth.social.pipeline.disconnect.allowed_to_disconnect',

    # Collects the social associations to disconnect.
    'anthill.framework.auth.social.pipeline.disconnect.get_entries',

    # Revoke any access_token when possible.
    'anthill.framework.auth.social.pipeline.disconnect.revoke_tokens',

    # Removes the social associations.
    'anthill.framework.auth.social.pipeline.disconnect.disconnect'
]
