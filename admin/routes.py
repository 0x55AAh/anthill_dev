# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.handlers import LogStreamingHandler
from admin import handlers


route_patterns = [
    url(r'^/?$', handlers.HomeHandler, name='admin'),
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/debug/?$', handlers.DebugHandler, name='debug'),
]

route_patterns += [
    url(r'^/chat/?$', handlers.TestMessengerHandler, name='chat')
]
