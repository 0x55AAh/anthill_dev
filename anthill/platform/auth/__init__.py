from anthill.framework.core.mail.asynchronous import send_mail
from anthill.platform.core.messenger.message import send_message
from anthill.platform.core.messenger.settings import messenger_settings
from anthill.platform.api.internal import RequestError, connector
from tornado.escape import json_decode
from functools import partial
import dateutil.parser
import logging

logger = logging.getLogger('anthill.application')


def filter_dict(data, exclude=None):
    if exclude:
        return dict(filter(lambda x: x[0] not in exclude, data.items()))
    return data


def iso_parse(s):
    return dateutil.parser.parse(s) if isinstance(s, str) else s


class RemoteUser:
    """
    User model is stored on dedicated service named `login`.
    So, when we deal with user request to some service,
    we need to get user info from remote service to use it locally.
    That's why the RemoteUser need.
    """
    USERNAME_FIELD = 'username'

    def __init__(self, username: str, email: str, **kwargs):
        kwargs['created'] = iso_parse(kwargs.pop('created', None))
        kwargs['last_login'] = iso_parse(kwargs.pop('last_login', None))
        self.__dict__.update(kwargs)
        self.username = username
        self.email = email

    def __str__(self):
        return self.get_username()

    def __repr__(self):
        return '<RemoteUser(name=%r)>' % self.get_username()

    def to_dict(self, exclude=None):
        d = self.__dict__.copy()
        profile = getattr(self, 'profile', None)
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

    async def send_mail(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        await send_mail(subject, message, from_email, [self.email], **kwargs)

    async def send_message(self, message, callback=None, client=None, content_type=None):
        """Send a message to this user."""
        create_personal_group = messenger_settings.PERSONAL_GROUP_FUNCTION
        data = {
            'data': message,
            'group': create_personal_group(self.id),
            'content_type': content_type,
            'trusted': True,
        }
        await send_message(
            event='create_message',
            data=data,
            callback=callback,
            client=client
        )


class RemoteProfile:
    """
    Profile model is stored on dedicated service named `profile`.
    So, when we deal with user request to some service,
    we need to get user profile info from remote service to use it locally.
    That's why the RemoteProfile need.
    """

    def __init__(self, user: RemoteUser, **kwargs):
        kwargs['payload'] = json_decode(kwargs.pop('payload', '{}'))
        self.__dict__.update(kwargs)
        self.user = user

    def __str__(self):
        return self.user.get_username()

    def __repr__(self):
        return '<RemoteProfile(name=%r)>' % self.user.get_username()

    def to_dict(self, exclude=None):
        d = self.__dict__.copy()
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
