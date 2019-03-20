# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include
from admin.handlers import apigw as handlers, LogRequestHandler


_route_patterns = [
    url(r'^/?$', handlers.IndexHandler, name='index'),
    url(r'^/log/?$', LogRequestHandler, {'service_name': 'apigw'}, name='log')
]

route_patterns = [
    url(r'^/apigw/', include(_route_patterns, namespace='apigw')),
]
