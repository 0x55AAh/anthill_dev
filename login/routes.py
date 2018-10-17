# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from login import handlers
from discovery.api.compat.rest import routes as rest_routes
from anthill.framework.auth.social import routes as social_auth_routes
from anthill.framework.utils.urls import include


route_patterns = [
    url(r'^/', include(rest_routes.route_patterns, namespace='api')),  # for compatibility only
    url(r'^/social/', include(social_auth_routes.route_patterns, namespace='social')),
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/register/?$', handlers.RegisterHandler, name='register'),
]
