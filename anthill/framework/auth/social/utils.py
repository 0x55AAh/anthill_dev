from social_core.utils import setting_name, get_strategy
from social_core.backends.utils import get_backend
from functools import wraps


DEFAULTS = {
    'social_auth_storage': 'anthill.framework.auth.social.models.TornadoStorage',
    'social_auth_strategy': 'anthill.framework.auth.social.strategy.TornadoStrategy'
}


def get_helper(request_handler, name):
    return request_handler.settings.get(
        setting_name(name), DEFAULTS.get(name, None))


def load_strategy(request_handler):
    strategy = get_helper(request_handler, 'social_auth_strategy')
    storage = get_helper(request_handler, 'social_auth_storage')
    return get_strategy(strategy, storage, request_handler)


def load_backend(request_handler, strategy, name, redirect_uri):
    backends = get_helper(request_handler, 'authentication_backends')
    backend = get_backend(backends, name)
    return backend(strategy, redirect_uri)


def psa(redirect_uri=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, backend, *args, **kwargs):
            uri = redirect_uri
            if uri and not uri.startswith('/'):
                uri = self.reverse_url(uri, backend)
            self.strategy = load_strategy(self)
            self.backend = load_backend(self, self.strategy, backend, uri)
            return func(self, backend, *args, **kwargs)
        return wrapper
    return decorator
