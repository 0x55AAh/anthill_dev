"""
Google OpenId, OAuth2, OAuth1, Google+ Sign-in backends, docs at:
    https://python-social-auth.readthedocs.io/en/latest/backends/google.html
"""
from social_core.backends import google


# noinspection PyAbstractClass
class GoogleOAuth2(google.GoogleOAuth2):
    """Google OAuth2 authentication backend."""


# noinspection PyAbstractClass
class GooglePlusAuth(google.GooglePlusAuth):
    pass


# noinspection PyAbstractClass
class GoogleOAuth(google.GoogleOAuth):
    """Google OAuth authorization mechanism."""


class GoogleOpenId(google.GoogleOpenId):
    pass
