from anthill.framework.utils.crypto import constant_time_compare
from anthill.framework.auth import (
    _get_user_session_key,
    _get_backends,
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    load_backend
)
from anthill.framework.auth.models import AnonymousUser
from anthill.framework.conf import settings


__all__ = [
    'UserHandlerMixin',
    'LoginHandlerMixin',
    'LogoutHandlerMixin',
    'AuthHandlerMixin'
]


class UserHandlerMixin:
    async def get_user(self):
        """
        Return the user model instance associated with the given session.
        If no user is retrieved, return an instance of `AnonymousUser`.
        """
        user = None
        try:
            user_id = _get_user_session_key(self)
            backend_path = self.session[BACKEND_SESSION_KEY]
        except KeyError:
            pass
        else:
            if backend_path in settings.AUTHENTICATION_BACKENDS:
                backend = load_backend(backend_path)
                user = await backend.get_user(user_id)
                # Verify the session
                if hasattr(user, 'get_session_auth_hash'):
                    session_hash = self.session.get(HASH_SESSION_KEY)
                    session_hash_verified = session_hash and constant_time_compare(
                        session_hash,
                        user.get_session_auth_hash()
                    )
                    if not session_hash_verified:
                        self.session.flush()
                        user = None

        return user or AnonymousUser()

    # noinspection PyAttributeOutsideInit
    async def setup_user(self):
        self.current_user = await self.get_user()


class LoginHandlerMixin:
    # noinspection PyAttributeOutsideInit
    def login(self, user, backend=None):
        """
        Persist a user id and a backend in the request. This way a user doesn't
        have to reauthenticate on every request. Note that data set during
        the anonymous session is retained when the user logs in.
        """
        session_auth_hash = ''
        if user is None:
            user = self.current_user
        if hasattr(user, 'get_session_auth_hash'):
            session_auth_hash = user.get_session_auth_hash()

        if SESSION_KEY in self.session:
            if _get_user_session_key(self) != user.id or (
                    session_auth_hash and
                    not constant_time_compare(self.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
                # To avoid reusing another user's session, create a new, empty
                # session if the existing session corresponds to a different
                # authenticated user.
                self.session.flush()
        else:
            self.session.cycle_key()

        try:
            backend = backend or user.backend
        except AttributeError:
            backends = _get_backends(return_tuples=True)
            if len(backends) == 1:
                _, backend = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument or set the '
                    '`backend` attribute on the user.'
                )
        else:
            if not isinstance(backend, str):
                raise TypeError('backend must be a dotted import path string (got %r).' % backend)

        self.session[SESSION_KEY] = user.id
        self.session[BACKEND_SESSION_KEY] = backend
        self.session[HASH_SESSION_KEY] = session_auth_hash
        self.current_user = user


class LogoutHandlerMixin:
    # noinspection PyAttributeOutsideInit
    def logout(self):
        if not isinstance(self.current_user, (AnonymousUser, type(None))):
            self.session.flush()
            self.current_user = AnonymousUser()


class AuthHandlerMixin(UserHandlerMixin, LoginHandlerMixin, LogoutHandlerMixin):
    pass
