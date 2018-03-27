# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from . import handlers

route_patterns = [
    url(r'/test/(\d+)', handlers.TestHandler, kwargs=None, name='test'),
    # (r'/test/(\d+)', handlers.TestHandler, None, 'test'),
]
