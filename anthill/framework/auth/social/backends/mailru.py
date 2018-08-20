"""
Mail.ru OAuth2 backend, docs at:
    https://python-social-auth.readthedocs.io/en/latest/backends/mailru.html
"""
from social_core.backends import mailru


# noinspection PyAbstractClass
class MailruOAuth2(mailru.MailruOAuth2):
    """Mail.ru authentication backend."""
