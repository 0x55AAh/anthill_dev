# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from admin.handlers import discovery as handlers

route_patterns = [
    url(r'^/?$', handlers.ServicesList, name='index'),
    url(r'^/(?P<name_detail>[^/]+)/detail/?$', handlers.ServiceDetail, name='detail'),
]
