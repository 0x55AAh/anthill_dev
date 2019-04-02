# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import social as handlers, LogRequestHandler


@root(pattern=r'^/social/', namespace='social')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'social'}, name='log')
    ]
