# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from anthill.framework.utils.urls import include
from anthill.framework.utils.module_loading import import_module
from anthill.framework.handlers import TemplateHandler
from admin import handlers
from tornado.web import url
import itertools

extra_routes = (
    'admin.routes.apigw',
    'admin.routes.config',
    'admin.routes.discovery',
    'admin.routes.dlc',
    'admin.routes.environment',
    'admin.routes.event',
    'admin.routes.exec',
    'admin.routes.game_master',
    'admin.routes.leaderboard',
    'admin.routes.log',
    'admin.routes.login',
    'admin.routes.media',
    'admin.routes.message',
    'admin.routes.profile',
    'admin.routes.promo',
    'admin.routes.report',
    'admin.routes.social',
    'admin.routes.store',
)
extra_routes = map(import_module, extra_routes)
extra_route_patterns = map(lambda mod: getattr(mod, 'route_patterns', []), extra_routes)

service_route_patterns = [
                             url(r'^/?$', handlers.ServiceRequestHandler, name='index'),
                             url(r'^/log/?$', handlers.LogRequestHandler, name='log'),
                         ] + list(itertools.chain.from_iterable(extra_route_patterns))

route_patterns = [
    url(r'^/?$', handlers.HomeHandler, name='index'),
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/settings/?$', handlers.SettingsRequestHandler, name='settings'),
    url(r'^/audit-log/?$', handlers.AuditLogRequestHandler, name='audit-log'),
    url(r'^/profile/?$', handlers.ProfileRequestHandler, name='profile'),
    url(r'^/debug/?$', handlers.DebugHandler, name='debug'),
    url(r'^/debug-session/?$', handlers.DebugSessionHandler, name='debug-session'),
    url(r'^/utils-session/?$', handlers.UtilsSessionHandler, name='utils-session'),
    url(r'^/robots.txt$', TemplateHandler,
        dict(template_name='robots.txt', content_type='text/plain'), name='robots.txt'),
    url(r'^/update-manager/?$', handlers.UpdateManagerRequestHandler, name='update-manager'),
    url(r'^/sidebar-main-toggle/?$', handlers.SidebarMainToggle, name='sidebar-main-toggle'),
    url(r'^/services/(?P<name>[^/]+)/', include(service_route_patterns, namespace='service')),
]
