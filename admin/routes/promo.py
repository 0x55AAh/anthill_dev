# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import promo as handlers, LogRequestHandler


@root(pattern=r'^/promo/', namespace='promo')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/(?P<promo_code_id>[^/]+)/?$', handlers.PromoCodeDetailHandler, name='promo_code_detail'),
        url(r'^/log/?$', LogRequestHandler, {'service_name': 'promo'}, name='log')
    ]
