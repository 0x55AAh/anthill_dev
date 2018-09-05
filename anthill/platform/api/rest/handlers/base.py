from tornado.web import HTTPError
from anthill.framework.handlers import RequestHandler, JSONHandlerMixin
from anthill.framework.utils.translation import translate as _
import logging


logger = logging.getLogger('anthill.application')


# 200 – OK – All is working, normal answer for any ordinary request
# 201 – OK – Returned if resource was created successfully (POST or PUT)
# 204 – OK – Returned if resource was deleted successfully (DELETE)
# 304 – Not Modified – Resource was not modified
# 400 – Bad Request – Wrong request or request couldn't be served.
# 401 – Unauthorized – Authorization required for this resource
# 403 – Forbidden – Not enough permissions for this resource
# 404 – Not found
# 422 – Unprocessable Entity – Server couldn't serve this request because there is not enough data
# 500 – Internal Server Error – Internal server error. Normally doesn't show up )
http_statuses = {
    'OK': {'code': 200, 'message': _('OK')},
    'CREATED': {'code': 201, 'message': _('Successfully created/updated content')},
    'NO_CONTENT': {'code': 204, 'message': _('Request is ok, but response body is empty')},
    'NOT_MODIFIED': {'code': 304, 'message': _('Resource not modified')},
    'HIDDEN_ERR': {'code': 400, 'message': _('You\'re not allowed to do this kind of things. %s')},
    'ANY_ERR': {'code': 400, 'message': _('An error occurred because you\'ve passed incorrect data.')},
    'WRONG_FILENAME': {'code': 400, 'message': _('Wrong filename was given')},
    'WRONG_CREDENTIALS': {'code': 403, 'message': _('Your access token is not valid to access content')},
    'NO_OBJECT_FOUND': {'code': 404, 'message': _('There is no requested <object> in a system')},
    'NO_MEDIA_FOUND': {'code': 404, 'message': _('There is no requested <media> in a system')},
    'NO_CUR_BIKE': {
        'code': 404, 'message': _('You can only operate with currently selected bike, nothing is selected now')},
    'METHOD_NOT_ALLOWED': {'code': 405, 'message': _('A request method is not supported for the requested resource.')},
    'WRONG_PARAM': {'code': 409, 'message': _('Wrong parameter(s) was(were) passed in request')},
    'WRONG_REQUEST': {'code': 409, 'message': _('Wrong formed request, no conditions available to complete it')},
    'NOT_ENOUGH_PARAM': {'code': 409, 'message': _('Not enough params were given to complete the request')},
    'WRONG_PARAM_WITH_EXC': {'code': 422, 'message': _('Wrong parameter(s) was(were) passed in request. %s')},
    'DUPLICATE_IN_DB': {
        'code': 422, 'message': _('There is already an entry in DB with equal value(s), must be unique. %s')},
    'SRV_INTERNAL_ERR': {'code': 500, 'message': _('Core server error has occurred. We are soooo sorry :(')},
    'NOT_IMPLEMENTED': {'code': 500, 'message': _('Request is ok, but server has no implementation for this method')},
}


class APIHandler(JSONHandlerMixin, RequestHandler):
    schema_class = None

    def get_schema_class(self):
        return self.schema_class

    def get_schema(self):
        schema_class = self.get_schema_class()
        return schema_class()

    def serialize(self, data):
        return data

    def get(self, *args, **kwargs):
        """Default 404 code for not implemented GET-method."""
        logger.warning('Access to not implemented GET method')
        raise HTTPError(
            status_code=http_statuses['NO_OBJECT_FOUND']['code'],
            log_message=http_statuses['NO_OBJECT_FOUND']['message'])

    def write_json(self, status_code: int=200, message: str=None, data: any=None) -> None:
        """
        Writes json response to client, decoding `data` to json with HTTP-header.

        :param status_code: HTTP response code
        :param message: status code message
        :param data: data to pass to client
        :return:
        """
        self.set_header('Content-Type', 'application/json')
        self.set_status(status_code, message)
        if status_code == 204:
            # status code expects no body
            self.finish()
        else:
            result = {
                'meta': {
                    'code': self._status_code,
                    'message': self._reason,
                },
                'data': data,
            } if status_code != 204 else None
            self.finish(self.dumps(result))
