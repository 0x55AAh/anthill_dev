# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include
from admin.handlers import discovery as handlers, LogRequestHandler


_route_patterns = [
    url(r'^/?$', handlers.IndexHandler, name='index'),
    url(r'^/(?P<service_name>[^/]+)/?$', handlers.ServiceDetail, name='service'),
    url(r'^/log/?$', LogRequestHandler, {'service_name': 'discovery'}, name='log')
]

route_patterns = [
    url(r'^/discovery/', include(_route_patterns, namespace='discovery')),
]
