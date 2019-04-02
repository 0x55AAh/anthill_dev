# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import LogRequestHandler, HomeHandler


@root(pattern=r'^/admin/', namespace='admin')
def route_patterns():
    return [
        url(r'^/?$', HomeHandler, name='index'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'admin'}, name='log')
    ]
