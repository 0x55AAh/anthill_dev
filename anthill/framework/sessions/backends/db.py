import logging

from anthill.framework.sessions.backends.base import (
    CreateError, SessionBase, UpdateError,
)
from anthill.framework.core.exceptions import SuspiciousOperation


class SessionStore(SessionBase):
    """
    Implement database session store.
    """

    def __init__(self, session_key=None):
        super().__init__(session_key)

    def exists(self, session_key):
        pass

    def create(self):
        pass

    def save(self, must_create=False):
        pass

    def delete(self, session_key=None):
        pass

    def load(self):
        pass

    @classmethod
    def clear_expired(cls):
        pass
