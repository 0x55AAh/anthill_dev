# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from . import handlers


route_patterns = [
    url(r'^/(?P<app_name>[^/]+)/(?P<app_version>[^/]+)/?$', handlers.DiscoverHandler, name='discover'),
]
