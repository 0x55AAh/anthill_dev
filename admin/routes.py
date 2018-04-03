# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from . import handlers


route_patterns = [
    url(r'^/?$', handlers.HomeHandler, kwargs=None, name='admin'),
    url(r'^/login/?$', handlers.LoginHandler, kwargs=None, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, kwargs=None, name='logout'),
]
