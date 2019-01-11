# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from message import handlers
from anthill.framework.handlers.socketio import socketio_server
from anthill.platform.core.messenger.handlers.transports import socketio

socketio_server.register_namespace(handlers.MessengerNamespace('/messenger'))

route_patterns = [
    url(r'^/messenger/?$', handlers.MessengerHandler, name='messenger'),
    url(r'^/socket.io/$', socketio.MessengerHandler),
]
