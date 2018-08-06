# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from . import handlers
from discovery.api.compat.rest import routes as rest_routes
from anthill.framework.utils.urls import include

# Create your routes here.
route_patterns = [
    url(r'^/', include(rest_routes.route_patterns, namespace='api')),  # for compatibility only
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/register/?$', handlers.RegisterHandler, name='register'),
]
