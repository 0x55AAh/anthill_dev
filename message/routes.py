# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from message import handlers


route_patterns = [
    url(r'^/messenger/?$', handlers.MessengerHandler, name='messenger'),
]
