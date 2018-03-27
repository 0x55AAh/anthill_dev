from microservices_framework.apps import app


def reverse(name, *args, **kwargs):
    """Returns a URL path for handler named ``name``"""
    return app.reverse_url(name, *args, **kwargs)


def resolve(path):
    """Returns a route attributes dict for path ``path``"""
    return app.resolve_url(path)
