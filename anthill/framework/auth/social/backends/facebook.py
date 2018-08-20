"""
Facebook OAuth2 and Canvas Application backends, docs at:
    https://python-social-auth.readthedocs.io/en/latest/backends/facebook.html
"""
from social_core.backends import facebook


# noinspection PyAbstractClass
class FacebookOAuth2(facebook.FacebookOAuth2):
    """Facebook OAuth2 authentication backend."""


class FacebookAppOAuth2(facebook.FacebookAppOAuth2):
    """Facebook Application Authentication support."""
