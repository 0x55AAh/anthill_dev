# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import dlc as handlers, LogRequestHandler


@root(pattern=r'^/dlc/', namespace='dlc')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'dlc'}, name='log')
    ]
