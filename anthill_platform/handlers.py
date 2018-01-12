from tornado.web import RequestHandler


class BaseRequestHandler(RequestHandler):
    def data_received(self, chunk):
        pass
