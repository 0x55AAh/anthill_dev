# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include
from admin.handlers import dlc as handlers, LogRequestHandler


_route_patterns = [
    url(r'^/?$', handlers.IndexHandler, name='index'),
    url(r'^/log/?$', LogRequestHandler, {'service_name': 'dlc'}, name='log')
]

route_patterns = [
    url(r'^/dlc/', include(_route_patterns, namespace='dlc')),
]
