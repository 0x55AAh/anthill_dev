# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from admin.handlers import discovery as handlers

route_patterns = [
    # url(r'^/services/?$', handlers.ServicesList, name='services-list'),
    url(r'^/?$', handlers.ServicesList, name='index'),
    url(r'^/services/(?P<name_detail>[^/]+)/?$', handlers.ServiceDetail, name='service-detail'),
]
