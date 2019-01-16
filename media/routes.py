# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from media import handlers

route_patterns = [
    url(r'/upload/?', handlers.UploadHandler, name='upload'),
]
