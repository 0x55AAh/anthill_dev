from anthill.framework.apps import app
from .functional import lazy


def reverse(name, *args, **kwargs):
    """Returns a URL path for handler named ``name``"""
    url = app.reverse_url(name, *args, **kwargs)
    return url[:-1] if url.endswith('?') else url


def resolve(path):
    """Returns a route attributes dict for path ``path``"""
    return app.resolve_url(path)


reverse_lazy = lazy(reverse, str)
