from anthill.framework.auth.social.core.backends import base


# noinspection PyAbstractClass
class BaseAuth(base.BaseAuth):
    """
    A authentication backend that authenticates the user based on
    the provider response.
    """
