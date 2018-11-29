from anthill.platform.auth.handlers import UserRequestHandler
from admin.handlers._base import ServiceContextMixin


class ServicesList(ServiceContextMixin, UserRequestHandler):
    pass


class ServiceDetail(ServiceContextMixin, UserRequestHandler):
    pass
