from anthill.platform.api.internal import InternalConnection
from functools import partial


DISCOVERY = 'discovery'


internal_connection = InternalConnection()
internal_request = internal_connection.request
discovery_request = partial(internal_request, DISCOVERY)
