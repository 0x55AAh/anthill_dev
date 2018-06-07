from anthill.framework.handlers import RequestHandler, TemplateMixin
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql.type.schema import GraphQLSchema
from anthill.framework.conf import settings
from tornado.escape import json_decode, json_encode
from graphql.error import GraphQLError, format_error
from anthill.framework.http import HttpForbiddenError, HttpBadRequestError
from tornado.log import app_log
from functools import wraps
from tornado.web import HTTPError
import traceback
import inspect
import importlib
import six
import sys


DEFAULTS = {
    'SCHEMA': None,
    'SCHEMA_OUTPUT': 'schema.json',
    'SCHEMA_INDENT': None,
    'MIDDLEWARE': (),
    # Set to True if the connection fields must have
    # either the first or last argument
    'RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST': False,
    # Max items returned in ConnectionFields / FilterConnectionFields
    'RELAY_CONNECTION_MAX_LIMIT': 100,
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'MIDDLEWARE',
    'SCHEMA',
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = "Could not import '%s' for Graphene setting '%s'. " \
              "%s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class GrapheneSettings:
    """
    A settings object, that allows API settings to be accessed as properties.
    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'GRAPHENE', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Graphene setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        setattr(self, attr, val)
        return val


graphene_settings = GrapheneSettings(None, DEFAULTS, IMPORT_STRINGS)


def instantiate_middleware(middlewares):
    for middleware in middlewares:
        if inspect.isclass(middleware):
            yield middleware()
            continue
        yield middleware


def error_status(exception):
    if isinstance(exception, HTTPError):
        return exception.status_code
    elif isinstance(exception, (ExecutionError, GraphQLError)):
        return 400
    else:
        return 500


def error_format(exception):
    if isinstance(exception, ExecutionError):
        return [{'message': e} for e in exception.errors]
    elif isinstance(exception, GraphQLError):
        return [format_error(exception)]
    elif isinstance(exception, HTTPError):
        return [{'message': exception.log_message,
                 'reason': exception.reason}]
    else:
        return [{'message': 'Unknown server error'}]


def error_response(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            result = await func(self, *args, **kwargs)
        except Exception as ex:
            if not isinstance(ex, (HTTPError, ExecutionError, GraphQLError)):
                tb = ''.join(traceback.format_exception(*sys.exc_info()))
                app_log.error('Error: {0} {1}'.format(ex, tb))
            self.set_status(error_status(ex))
            error_json = json_encode({'errors': error_format(ex)})
            app_log.debug('error_json: %s', error_json)
            self.write(error_json)
        else:
            return result
    return wrapper


class ExecutionError(Exception):
    def __init__(self, status_code=400, errors=None):
        self.status_code = status_code
        if errors is None:
            self.errors = []
        else:
            self.errors = [str(e) for e in errors]
        self.message = '\n'.join(self.errors)


class GraphQLHandler(TemplateMixin, RequestHandler):
    SUPPORTED_METHODS = ('GET', 'POST')

    graphiql_template = 'graphene/graphiql.html'
    graphiql_version = '0.11.11'

    schema = None
    middleware = None
    graphiql = False
    executor = None
    root_value = None
    pretty = False
    batch = False

    def initialize(
            self,
            graphiql_template=None,
            graphiql_version=None,
            schema=None,
            middleware=None,
            graphiql=False,
            executor=None,
            root_value=None,
            pretty=False,
            batch=False):
        super().initialize(graphiql_template)
        if not schema:
            schema = graphene_settings.SCHEMA
        if middleware is None:
            middleware = graphene_settings.MIDDLEWARE
        if middleware is not None:
            self.middleware = list(instantiate_middleware(middleware))
        if not executor:
            executor = AsyncioExecutor()
        self.graphiql_version = graphiql_version
        self.schema = self.schema or schema
        self.graphiql = self.graphiql or graphiql
        self.executor = self.executor or executor
        self.root_value = root_value
        self.pretty = pretty
        self.batch = batch

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.template_name = self.graphiql_template
        self.enable_async = isinstance(self.executor, AsyncioExecutor)
        assert isinstance(self.schema, GraphQLSchema), \
            'A Schema is required to be provided to %s.' % self.__class__.__name__
        assert isinstance(self.executor, AsyncioExecutor), \
            'An executor is required to be subclassed from `AsyncioExecutor`.'
        assert not all((self.graphiql, self.batch)), \
            'Use either graphiql or batch processing'

    @error_response
    async def post(self):
        data = self.parse_body()
        if self.batch:
            responses = []
            for entry in data:
                responses.append(await self.get_graphql_response(entry))
            result = '[{}]'.format(','.join([response[0] for response in responses]))
            status_code = responses and max(responses, key=lambda response: response[1])[1] or 200
        else:
            result, status_code = await self.get_graphql_response(data)
        self.set_status(status_code)
        self.write(result)

    async def get(self):
        if self.is_graphiql():
            return self.render()
        raise HttpForbiddenError('Method `GET` not allowed.')

    def is_graphiql(self):
        return all([
            self.graphiql,
            self.request.method.lower() == 'get',
            'raw' not in self.request.query_arguments,
            settings.DEBUG,
            any([
                'text/html' in self.request.headers.get('accept', {}),
                '*/*' in self.request.headers.get('accept', {}),
            ]),
        ])

    def is_pretty(self):
        return any([
            self.pretty,
            self.is_graphiql(),
            # self.request.query_arguments('pretty')
        ])

    async def get_graphql_response(self, data):
        query, variable_values, operation_name, id_ = self.get_graphql_params(data)
        execution_result = await self.execute_graphql_request(query, variable_values, operation_name)

        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                ex = ExecutionError(errors=execution_result.errors)
                app_log.warn('GraphQL Error: %s', ex)
                raise ex

            if execution_result.invalid:
                status_code = 400
            else:
                response['data'] = execution_result.data

            if self.batch:
                response['id'] = id_
                response['status'] = status_code

            result = json_encode(response)
        else:
            result = None

        return result, status_code

    async def execute_graphql_request(self, query, variable_values, operation_name):
        result = await self.schema.execute(
            query,
            variable_values=variable_values,
            operation_name=operation_name,
            context_value=self.get_context(),
            middleware=self.middleware,
            return_promise=self.enable_async,
            root_value=self.root_value,
            executor=self.executor
        )
        return result

    def get_graphql_params(self, data):
        id_ = data.get('id')
        query = data.get('query')

        variables = data.get('variables')
        if variables and isinstance(variables, six.text_type):
            try:
                variables = json_decode(variables)
            except Exception:
                raise HttpBadRequestError('Variables are invalid JSON.')

        operation_name = data.get('operationName')
        if operation_name == 'null':
            operation_name = None

        return query, variables, operation_name, id_

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        namespace.update(graphiql_version=self.graphiql_version)
        return namespace

    def parse_body(self):
        content_type = self.get_content_type()

        if content_type == 'application/json':
            request_json = json_decode(self.request.body)
            if self.batch:
                assert isinstance(request_json, list), (
                    'Batch requests should receive a list, but received {}.'
                ).format(repr(request_json))
                assert len(request_json) > 0, (
                    'Received an empty list in the batch request.'
                )
            else:
                assert isinstance(request_json, dict), (
                    'The received data is not a valid JSON query.'
                )
            return request_json

        return {}

    def get_content_type(self):
        content_type = self.request.headers.get('Content-Type', 'text/plain')
        return content_type.split(';', 1)[0].lower()

    def get_context(self):
        return self.request
