# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from . import handlers
from anthill.framework.handlers import LogStreamHandler


route_patterns = [
    url(r'^/?$', handlers.HomeHandler, name='admin'),
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/debug/?$', handlers.DebugHandler, name='debug'),
    url(r'^/chat/?$', handlers.TestMessengerHandler, name='chat'),
    url(r'^/log/?$', LogStreamHandler, kwargs=dict(handler_name='anthill'), name='log'),
]
