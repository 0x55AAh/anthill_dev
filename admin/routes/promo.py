# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from admin.handlers import promo as handlers

route_patterns = [
    url(r'^/?$', handlers.PromoCodeList, name='promo_index'),
    url(r'^/(?P<name_detail>[^/]+)/?$', handlers.PromoCodeDetail, name='promo_code_detail'),
]
