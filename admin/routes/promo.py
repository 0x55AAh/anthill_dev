# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include
from admin.handlers import promo as handlers, LogRequestHandler


_route_patterns = [
    url(r'^/?$', handlers.IndexHandler, name='index'),
    url(r'^/(?P<name_detail>[^/]+)/?$', handlers.PromoCodeDetailHandler, name='promo_code_detail'),
    url(r'^/log/?$', LogRequestHandler, {'service_name': 'promo'}, name='log')
]

route_patterns = [
    url(r'^/promo/', include(_route_patterns, namespace='promo')),
]
