"""
VK.com OpenAPI, OAuth2 and Iframe application OAuth2 backends, docs at:
    https://python-social-auth.readthedocs.io/en/latest/backends/vk.html
"""
from social_core.backends import vk


# noinspection PyAbstractClass
class VKontakteOpenAPI(vk.VKontakteOpenAPI):
    """VK.COM OpenAPI authentication backend."""


# noinspection PyAbstractClass
class VKOAuth2(vk.VKOAuth2):
    """VKOAuth2 authentication backend."""


# noinspection PyAbstractClass
class VKAppOAuth2(vk.VKAppOAuth2):
    """VK.com Application Authentication support."""
