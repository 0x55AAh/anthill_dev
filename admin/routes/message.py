# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import message as handlers, LogRequestHandler


@root(pattern=r'^/message/', namespace='message')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/groups/?$', handlers.IndexHandler, name='message_group_list'),
        url(r'^/groups/(?P<group_id>[^/]+)/?$', handlers.GroupDetailHandler, name='message_group_detail'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'message'}, name='log')
    ]
