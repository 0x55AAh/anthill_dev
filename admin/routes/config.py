# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import config as handlers, LogRequestHandler


@root(pattern=r'^/config/', namespace='config')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'config'}, name='log')
    ]
