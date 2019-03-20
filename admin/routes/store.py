# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include
from admin.handlers import store as handlers, LogRequestHandler


_route_patterns = [
    url(r'^/?$', handlers.IndexHandler, name='index'),
    url(r'^/log/?$', LogRequestHandler, {'service_name': 'store'}, name='log')
]

route_patterns = [
    url(r'^/store/', include(_route_patterns, namespace='store')),
]
