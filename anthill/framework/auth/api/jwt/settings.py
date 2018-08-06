from anthill.framework.conf import settings


USER_SETTINGS = getattr(settings, 'JWT_AUTH', None)


