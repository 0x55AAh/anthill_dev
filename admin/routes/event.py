# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import event as handlers, LogRequestHandler


@root(pattern=r'^/event/', namespace='event')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),

        url(r'^/(?P<event_id>[^/]+)/?$', handlers.EventDetailHandler, name='event_detail'),
        url(r'^/(?P<event_id>[^/]+)/participants/?$', handlers.ParticipantListHandler, name='participant_list'),
        url(r'^/(?P<event_id>[^/]+)/participants/(?P<user_id>[^/]+)/?$', handlers.ParticipantDetailHandler,
            name='participant_detail'),

        url(r'^/generator_pools/?$', handlers.GeneratorPoolListHandler, name='generator_pool_list'),
        url(r'^/generator_pools/(?P<generator_pool_id>[^/]+)/?$', handlers.GeneratorPoolDetailHandler,
            name='generator_pool_detail'),

        url(r'^/generators/?$', handlers.GeneratorListHandler, name='generator_list'),
        url(r'^/generators/(?P<generator_id>[^/]+)/?$', handlers.GeneratorDetailHandler, name='generator_detail'),

        url(r'^/categories/?$', handlers.CategoryListHandler, name='category_list'),
        url(r'^/categories/(?P<category_id>[^/]+)/?$', handlers.CategoryDetailHandler, name='category_detail'),

        url(r'^/log/?$', LogRequestHandler, {'service_name': 'event'}, name='log')
    ]
