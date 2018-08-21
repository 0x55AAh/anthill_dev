from anthill.platform.api.internal import InternalConnection
from functools import partial


DISCOVERY = 'discovery'


internal_connection = InternalConnection()
internal_request = internal_connection.request
discovery_request = partial(internal_request, DISCOVERY)


class InternalRequestMixin:
    service = None
    connection_class = InternalConnection

    def get_connection(self):
        return self.connection_class()

    @property
    def internal_request(self):
        if self.service is not None:
            return partial(self.get_connection().request, self.service)
        return self.get_connection().request


class InternalRequest(InternalRequestMixin):
    def __init__(self, service=None):
        self.service = service
