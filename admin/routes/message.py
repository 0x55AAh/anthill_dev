# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include
from admin.handlers import message as handlers, LogRequestHandler


_route_patterns = [
    url(r'^/?$', handlers.IndexHandler, name='index'),
    url(r'^/log/?$', LogRequestHandler, {'service_name': 'message'}, name='log')
]

route_patterns = [
    url(r'^/message/', include(_route_patterns, namespace='message')),
]
