from datetime import datetime
from typing import Optional


class RemoteUser:
    """
    User model is stored on dedicated service named `login`.
    So, when we deal with user request to some service,
    we need to get user info from remote service to use it locally.
    That's why the RemoteUser need.
    """
    USERNAME_FIELD = 'username'

    def __init__(self, id_: str, username: str, password: str,
                 created: datetime, last_login: datetime,
                 profile: Optional["RemoteProfile"]=None):
        self.id = id_
        self.username = username
        self.created = created
        self.last_login = last_login
        self.password = password
        self.profile = profile

    def __str__(self):
        return self.get_username()

    def __repr__(self):
        return '<RemoteUser(name=%r)>' % self.get_username()

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

    def get_porfile(self):
        return self.profile


class RemoteProfile:
    """
    Profile model is stored on dedicated service named `profile`.
    So, when we deal with user request to some service,
    we need to get user profile info from remote service to use it locally.
    That's why the RemoteProfile need.
    """
    def __init__(self, id_: str, user: "RemoteUser", payload: dict):
        self.id = id_
        self.user = user
        self.payload = payload
