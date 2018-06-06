from anthill.framework.handlers import RequestHandler, TemplateMixin
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql.type.schema import GraphQLSchema
from anthill.framework.conf import settings
from tornado.escape import json_decode, json_encode
from graphql.error import GraphQLError, format_error
from anthill.framework.http import HttpBadRequestError
from tornado.log import app_log
from functools import wraps
from tornado import web
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
        msg = "Could not import '%s' for Graphene setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class GrapheneSettings(object):
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
    if isinstance(exception, web.HTTPError):
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
    elif isinstance(exception, web.HTTPError):
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
            if not isinstance(ex, (web.HTTPError, ExecutionError, GraphQLError)):
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
    graphiql_template = 'graphene/graphiql.html'
    graphiql_version = '0.11.11'
    schema = None
    middleware = None
    graphiql = False
    executor = None
    root_value = None
    pretty = False
    batch = False
    enable_async = True

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
            batch=False,
            enable_async=True):
        super().initialize(graphiql_template)
        if not schema:
            schema = graphene_settings.SCHEMA
        if middleware is None:
            middleware = graphene_settings.MIDDLEWARE
        self.schema = self.schema or schema
        if middleware is not None:
            self.middleware = list(instantiate_middleware(middleware))
        self.graphiql = self.graphiql or graphiql
        self.executor = self.executor or executor or AsyncioExecutor()
        self.root_value = root_value
        self.pretty = pretty
        self.batch = batch
        self.enable_async = enable_async and isinstance(self.executor, AsyncioExecutor)

    def __init__(self, application, request, **kwargs):
        self.schema = None
        self.middleware = None
        self.graphiql = False
        self.executor = None
        self.root_value = None
        self.pretty = False
        self.batch = False
        self.enable_async = True
        self.template_name = self.graphiql_template
        super().__init__(application, request, **kwargs)
        assert isinstance(self.schema, GraphQLSchema), \
            'A Schema is required to be provided to %s.' % self.__class__.__name__
        assert isinstance(self.executor, AsyncioExecutor), \
            'An executor is required to be subclassed from `AsyncioExecutor`.'

    def options(self):
        self.set_status(204)
        self.finish()

    @error_response
    async def post(self):
        return await self.handle_graphql()

    def get(self):
        if self.is_graphiql():
            return self.render()

    def is_graphiql(self):
        return all([
            self.graphiql,
            self.request.method.lower() == 'get',
            'raw' not in self.request.query,
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
            self.request.query.get('pretty'),
        ])

    async def handle_graphql(self):
        result = await self.execute_graphql()
        if result and (result.errors or result.invalid):
            ex = ExecutionError(errors=result.errors)
            app_log.warn('GraphQL Error: %s', ex)
            raise ex

        response = {'data': result.data}
        self.write(json_encode(response))

    async def execute_graphql(self):
        data = self.parse_body()
        return await self.schema.execute(
            data.get('query'),
            variable_values=data.get('variables'),
            operation_name=data.get('operationName'),
            context_value=self.context,
            middleware=self.middleware,
            return_promise=self.enable_async,
            root_value=self.root_value,
            executor=self.executor
        )

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        namespace.update(graphiql_version=self.graphiql_version)
        return namespace

    def parse_body(self):
        content_type = self.get_content_type()

        if content_type == 'application/graphql':
            return {'query': self.request.body.decode()}

        elif content_type == 'application/json':
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

        elif content_type in ['application/x-www-form-urlencoded', 'multipart/form-data']:
            pass

        return {}

    def get_content_type(self):
        content_type = self.request.headers.get('Content-Type', 'text/plain')
        return content_type.split(';', 1)[0].lower()

    @property
    def context(self):
        return {}
