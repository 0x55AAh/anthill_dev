# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from message import handlers
from anthill.framework.handlers.socketio import sio
from anthill.platform.core.messenger.handlers.transports import socketio

sio.register_namespace(socketio.MessengerNamespace('/messenger'))

route_patterns = [
    url(r'^/messenger/?$', handlers.MessengerHandler, name='messenger'),
    url(r'^/socket.io/$', socketio.MessengerHandler),
]
