# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import bot as handlers, LogRequestHandler


@root(pattern=r'^/bot/', namespace='bot')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/(?P<bot_name>[^/]+)/?$', handlers.BotDetailHandler, name='detail'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'bot'}, name='log')
    ]
