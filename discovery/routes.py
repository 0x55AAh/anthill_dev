# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from discovery import handlers


route_patterns = [
    url(r'^/register-service/?$', handlers.RegisterService, name='register'),
    url(r'^/register-service/(?P<name>[^/]*)/?$', handlers.RegisterService, name='register-name'),
]
