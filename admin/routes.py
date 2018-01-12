from tornado.web import url
from . import handlers

route_patterns = [
    url(r'/test/', handlers.TestHandler, name='test'),
]
