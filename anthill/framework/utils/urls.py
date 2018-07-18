from anthill.framework.apps import app
from .functional import lazy


def reverse(name, *args, **kwargs):
    """Returns a URL path for handler named ``name``"""
    url = app.reverse_url(name, *args, **kwargs)
    return url.rstrip('?')


reverse_lazy = lazy(reverse, str)
