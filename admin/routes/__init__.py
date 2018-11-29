# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from anthill.framework.utils.urls import include
from anthill.framework.utils.module_loading import import_module
from admin import handlers
from tornado.web import url
import itertools

extra_routes = (
    'admin.routes.config',
    'admin.routes.discovery',
    'admin.routes.dlc',
    'admin.routes.exec',
    'admin.routes.login',
    'admin.routes.media',
    'admin.routes.message',
    'admin.routes.profile',
    'admin.routes.promo',
    'admin.routes.social',
    'admin.routes.store',
    'admin.routes.apigw',
)
extra_routes = map(import_module, extra_routes)
extra_routes = map(lambda mod: getattr(mod, 'route_patterns', []), extra_routes)
extra_routes = list(itertools.chain.from_iterable(extra_routes))

service_url_patterns = [
    url(r'^/?$', handlers.ServiceRequestHandler, name='service'),
    url(r'^/log/?$', handlers.LogRequestHandler, name='log'),
] + extra_routes

route_patterns = [
    url(r'^/?$', handlers.HomeHandler, name='index'),
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/settings/?$', handlers.SettingsRequestHandler, name='settings'),
    url(r'^/debug/?$', handlers.DebugHandler, name='debug'),
    url(r'^/debug-session/?$', handlers.DebugSessionHandler, name='debug-session'),
    url(r'^/sidebar-main-toggle/?$', handlers.SidebarMainToggle, name='sidebar-main-toggle'),
    url(r'^/services/(?P<name>[^/]+)/', include(service_url_patterns, namespace='service')),
]
