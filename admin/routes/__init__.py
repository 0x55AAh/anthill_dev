# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from admin.routes import (
    config, discovery, dlc, exec as exec_, login,
    message, profile, promo, social, store
)
from admin import handlers


route_patterns = [
    url(r'^/?$', handlers.HomeHandler, name='index'),
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/settings/?$', handlers.SettingsRequestHandler, name='settings'),
    url(r'^/debug/?$', handlers.DebugHandler, name='debug'),
    url(r'^/debug-session/?$', handlers.DebugSessionHandler, name='debug-session'),
    url(r'^/sidebar-main-toggle/?$', handlers.SidebarMainToggle, name='sidebar-main-toggle'),
    url(r'^/services/(?P<name>[^/]+)/?$', handlers.ServiceRequestHandler, name='service'),
]

for mod in (
    config, discovery, dlc, exec_, login,
    message, profile, promo, social, store
):
    route_patterns += getattr(mod, 'route_patterns', [])
