# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import environment as handlers, LogRequestHandler


@root(pattern=r'^/environment/', namespace='environment')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/(?P<environment_name>[^/]+)/?$', handlers.EnvironmentDetailHandler, name='detail'),
        url(r'^/applications/?$', handlers.ApplicationListHandler, name='applications'),
        url(r'^/applications/(?P<application_name>[^/]+)/?$',
            handlers.ApplicationDetailHandler, name='application'),
        url(r'^/applications/(?P<application_name>[^/]+)/(?P<application_version>[^/]+)/?$',
            handlers.ApplicationVersionDetailHandler, name='application_version'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'environment'}, name='log')
    ]
