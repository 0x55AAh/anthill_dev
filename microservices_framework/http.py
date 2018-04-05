from tornado.web import HTTPError as _HTTPError
from microservices_framework.utils.json import json


class HTTPError(_HTTPError):
    """Base HTTP exception class"""
    status_code = 500

    def __init__(self, log_message=None, *args, **kwargs):
        super(HTTPError, self).__init__(
            status_code=self.status_code, log_message=log_message, *args, **kwargs)


class HttpBadRequestError(HTTPError):
    status_code = 400


class HttpNotFoundError(HTTPError):
    status_code = 404


class HttpForbiddenError(HTTPError):
    status_code = 403


class HttpNotAllowedError(HTTPError):
    status_code = 405


class HttpGoneError(HTTPError):
    status_code = 410


class HttpServerError(HTTPError):
    pass


class Http404(HttpNotFoundError):
    pass


class JsonHandlerMixin:
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def dumps(self, data):
        return json.dumps(data, escape_forward_slashes=False)
