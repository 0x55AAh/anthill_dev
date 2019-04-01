# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include
from admin.handlers import bot as handlers, LogRequestHandler


_route_patterns = [
    url(r'^/?$', handlers.IndexHandler, name='index'),
    url(r'^/(?P<bot_name>[^/]+)/?$', handlers.BotDetailHandler, name='detail'),
    url(r'^/log/?$', LogRequestHandler, {'service_name': 'bot'}, name='log')
]

route_patterns = [
    url(r'^/bot/', include(_route_patterns, namespace='bot')),
]
