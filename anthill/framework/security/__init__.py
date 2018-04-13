from anthill.framework.utils.ip import get_ip, has_ip
from anthill.framework.conf import settings
from anthill.framework.http import Http404
from functools import wraps


def is_internal(ip):
    for internal_network in getattr(settings, 'INTERNAL_IPS', []):
        if has_ip(internal_network, ip):
            return True
    return False


def internal(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        ip = get_ip(self.request)
        if not is_internal(ip):
            # attacker shouldn't even know this page exists
            raise Http404
        return method(self, *args, **kwargs)
    return wrapper
