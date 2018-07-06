"""
Provides various authentication policies.
"""

import base64
import binascii
import jwt

from anthill.framework.auth import authenticate, get_user_model


class BaseAuthentication(object):
    """
    All authentication classes should extend BaseAuthentication.
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        raise NotImplementedError(".authenticate() must be overridden.")

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """


class BasicAuthentication(BaseAuthentication):
    """
    HTTP Basic authentication against username/password.
    """

    def authenticate(self, request):
        pass


class SessionAuthentication(BaseAuthentication):
    """
    Use Anthill's session framework for authentication.
    """

    def authenticate(self, request):
        pass


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".

    For example:
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    def authenticate(self, request):
        pass


class BaseJSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """

    def authenticate(self, request):
        pass


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the prefix.

    For example:
        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
