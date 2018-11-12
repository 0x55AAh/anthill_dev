from anthill.platform.api.internal import RequestError, connector
from datetime import datetime
from typing import Optional
from functools import partial
import logging


logger = logging.getLogger('anthill.application')


def filter_dict(data, exclude=None):
    if exclude:
        return dict(filter(lambda x: x[0] not in exclude, data.items()))
    return data


class RemoteUser:
    """
    User model is stored on dedicated service named `login`.
    So, when we deal with user request to some service,
    we need to get user info from remote service to use it locally.
    That's why the RemoteUser need.
    """
    USERNAME_FIELD = 'username'

    def __init__(self, username: str, password: str, **kwargs):
        self.__dict__.update(kwargs)
        self.username = username
        self.password = password

    def __str__(self):
        return self.get_username()

    def __repr__(self):
        return '<RemoteUser(name=%r)>' % self.get_username()

    def to_dict(self, exclude=None):
        profile = getattr(self, 'profile', None)
        d = self.__dict__
        if isinstance(profile, RemoteProfile):
            d['profile'] = profile.to_dict()
        else:
            d['profile'] = profile
        return filter_dict(d, exclude)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        """Return the identifying username for this RemoteUser."""
        return getattr(self, self.USERNAME_FIELD)

    def save(self):
        raise NotImplementedError("Service doesn't provide a DB representation for RemoteUser.")

    def delete(self):
        raise NotImplementedError("Service doesn't provide a DB representation for RemoteUser.")

    def set_password(self, raw_password):
        raise NotImplementedError("Service doesn't provide a DB representation for RemoteUser.")

    def check_password(self, raw_password):
        raise NotImplementedError("Service doesn't provide a DB representation for RemoteUser.")

    def get_profile(self):
        return getattr(self, 'profile', None)


class RemoteProfile:
    """
    Profile model is stored on dedicated service named `profile`.
    So, when we deal with user request to some service,
    we need to get user profile info from remote service to use it locally.
    That's why the RemoteProfile need.
    """
    def __init__(self, user: RemoteUser, **kwargs):
        self.__dict__.update(kwargs)
        self.user = user

    def __str__(self):
        return self.user.get_username()

    def __repr__(self):
        return '<RemoteProfile(name=%r)>' % self.user.get_username()

    def to_dict(self, exclude=None):
        d = self.__dict__
        d['user'] = self.user.to_dict()
        return filter_dict(d, exclude)


async def internal_authenticate(internal_request=None, **credentials) -> RemoteUser:
    """Perform internal api authentication."""
    internal_request = internal_request or connector.internal_request
    do_authenticate = partial(internal_request, 'login', 'authenticate')
    try:
        data = await do_authenticate(credentials=credentials)  # User data dict
    except RequestError as e:
        logger.error(str(e))
    else:
        return RemoteUser(**data)


async def internal_login(user_id, internal_request=None) -> str:
    """Perform internal api login."""
    internal_request = internal_request or connector.internal_request
    do_login = partial(internal_request, 'login', 'login')
    try:
        token = await do_login(user_id)
    except RequestError as e:
        logger.error(str(e))
    else:
        return token
