# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from . import handlers


route_patterns = [
    url(r'^/?$', handlers.HomeHandler, name='admin'),
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/debug/?$', handlers.DebugHandler, name='debug'),
    url(r'^/ws/?$', handlers.TestWSHandler, name='ws'),
    url(r'^/jws/?$', handlers.TestJWSHandler, name='jws'),
]
