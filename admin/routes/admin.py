# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include
from admin.handlers import LogRequestHandler, HomeHandler


_route_patterns = [
    url(r'^/?$', HomeHandler, name='index'),
    url(r'^/log/?$', LogRequestHandler, {'service_name': 'admin'}, name='log')
]

route_patterns = [
    url(r'^/admin/', include(_route_patterns, namespace='admin')),
]
