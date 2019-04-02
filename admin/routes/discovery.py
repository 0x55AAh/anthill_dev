# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import discovery as handlers, LogRequestHandler


@root(pattern=r'^/discovery/', namespace='discovery')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/(?P<service_name>[^/]+)/?$', handlers.ServiceDetail, name='service'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'discovery'}, name='log')
    ]
