from collections import defaultdict
from tornado.web import URLSpec
from anthill.framework.utils.text import slugify, camel_case_to_spaces, class_name
from anthill.framework.utils.module_loading import import_string
from anthill.platform.api.internal import api as internal_api
from anthill.framework.conf import settings
from urllib.parse import urlparse, urljoin
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins.property_mod_tracker import PropertyModTrackerPlugin
from sqlalchemy_continuum.plugins.transaction_changes import TransactionChangesPlugin
from sqlalchemy_continuum.plugins.activity import ActivityPlugin
from functools import lru_cache
from _thread import get_ident
import sqlalchemy as sa
import importlib
import logging
import re


logger = logging.getLogger('anthill.application')


class CommandNamesDuplicatedError(Exception):
    pass


class ApplicationExtensionNotRegistered(Exception):
    def __init__(self, extension):
        self.extension = extension


class Application:
    def __init__(self):
        self.settings = self.config = settings
        self.debug = settings.DEBUG
        self.name = settings.APPLICATION_NAME
        self.label = self.name.rpartition('.')[2]
        self.verbose_name = settings.APPLICATION_VERBOSE_NAME or self.label.title()
        self.description = settings.APPLICATION_DESCRIPTION
        self.icon_class = settings.APPLICATION_ICON_CLASS

        self.routes_conf = self.getdefault('ROUTES_CONF', '.'.join([self.name, 'routes']))
        self.service_class = self.getdefault('SERVICE_CLASS', '.'.join([self.name, 'services.Service']))
        self.management_conf = self.getdefault('MANAGEMENT_CONF', '.'.join([self.name, 'management']))
        self.models_conf = self.getdefault('MODELS_CONF', '.'.join([self.name, 'models']))
        self.ui_module = self.getdefault('UI_MODULE', '.'.join([self.name, 'ui']))

        self.internal = internal_api

        self.protocol, self.host, self.port = self.split_location()
        self.host_regex = r'^(%s)$' % re.escape(self.host)
        self.extensions = {}

        setattr(self, '__ident_func__', get_ident)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.label)

    def getdefault(self, key, default=None):
        return getattr(self.settings, key, None) or default

    def split_location(self):
        loc = urlparse(getattr(self.settings, 'LOCATION'))
        return loc.scheme, loc.hostname, loc.port

    @property
    def db(self):
        return self.get_extension('sqlalchemy').db

    @property
    def ma(self):
        return self.get_extension('marshmallow')

    @property
    def https_enabled(self):
        return self.protocol == 'https'

    @property
    def version(self):
        mod = importlib.import_module(self.name)
        return getattr(mod, 'version', None)

    @property
    def registry_entry(self):
        entry = {
            network: self.settings.LOCATION
            for network in self.settings.NETWORKS
        }
        entry.update(broker=settings.BROKER)
        return entry

    def get_extension(self, name):
        """Returns an extension by name or raise an exception."""
        if name not in self.extensions:
            raise ApplicationExtensionNotRegistered(name)
        return self.extensions[name]

    # noinspection PyProtectedMember,PyBroadException
    def get_models(self):
        classes, models, table_names = [], [], []
        for clazz in self.db.Model._decl_class_registry.values():
            try:
                table_names.append(clazz.__tablename__)
                classes.append(clazz)
            except Exception:
                pass
        for table in self.db.metadata.tables.items():
            if table[0] in table_names:
                models.append(classes[table_names.index(table[0])])
        return models

    # noinspection PyProtectedMember
    def get_model(self, name):
        return self.db.Model._decl_class_registry.get(name, None)

    # noinspection PyProtectedMember
    def get_model_by_tablename(self, tablename):
        for clazz in self.db.Model._decl_class_registry.values():
            if hasattr(clazz, '__tablename__') and clazz.__tablename__ == tablename:
                return clazz

    @property
    @lru_cache()
    def commands(self):
        def is_command_class(cls):
            from anthill.framework.core.management.commands import Command
            base_classes = (Command,)
            try:
                return issubclass(cls, base_classes) and cls not in base_classes
            except TypeError:
                return False

        def is_manager_instance(obj):
            from anthill.framework.core.management import Manager
            return isinstance(obj, Manager)

        def is_command(obj):
            return is_command_class(obj) or is_manager_instance(obj)

        def command_instance(obj):
            if is_manager_instance(obj):
                return obj
            return obj()

        def command_name(obj):
            nm = obj.__class__.__name__ if is_manager_instance(obj) else obj.__name__
            return getattr(obj, 'name', None) or slugify(camel_case_to_spaces(nm))

        def check_names(_commands):
            data = defaultdict(list)
            for name, instance in _commands:
                data[name].append(instance)
            for name, instances in data.items():
                if len(instances) > 1:
                    raise CommandNamesDuplicatedError(
                        '%s => %s' % (name, [obj.__class__.__name__ for obj in instances]))

        management = importlib.import_module(self.management_conf)

        commands = [
            (command_name(obj), command_instance(obj))
            for obj in management.__dict__.values()
            if is_command(obj)
        ]

        check_names(commands)

        return commands

    @property
    @lru_cache()
    def routes(self):
        """Returns routes map."""
        from anthill.framework.utils.urls import include, to_urlspec
        routes_mod = importlib.import_module(self.routes_conf)
        routes_list = getattr(routes_mod, 'route_patterns', [])
        routes_list = include(routes_list)
        new_routes_list = []
        for route in routes_list:
            route = to_urlspec(route)
            if route.name is None:
                route.name = class_name(route.target)
            new_routes_list.append(route)
        return new_routes_list

    @property
    def ui_modules(self):
        """
        Returns module object with UIModule subclasses and plain functions.
        Use for ``service.ui_modules`` and ``service.ui_methods`` initializing.
        """
        return importlib.import_module('.'.join([self.ui_module, 'modules']))

    def get_models_modules(self):
        sys_modules = ('anthill.framework.sessions.models',)
        if isinstance(self.models_conf, str):
            usr_modules = (self.models_conf,)
        elif isinstance(self.models_conf, (tuple, list)):
            usr_modules = self.models_conf
        else:
            usr_modules = ()
        return sys_modules + usr_modules

    def update_models(self):
        from marshmallow_sqlalchemy.convert import ModelConverter as BaseModelConverter
        from marshmallow_sqlalchemy import ModelConversionError, ModelSchema
        from sqlalchemy_jsonfield import JSONField
        from marshmallow import fields

        class ModelConverter(BaseModelConverter):
            """Anthill model converter for marshmallow model schema."""
            SQLA_TYPE_MAPPING = dict(
                list(BaseModelConverter.SQLA_TYPE_MAPPING.items()) +
                [(JSONField, fields.Str)]
            )

        def add_schema(cls):
            if hasattr(cls, '__tablename__'):
                if cls.__name__.endswith('Schema'):
                    raise ModelConversionError(
                        "For safety, setup_schema can not be used when a "
                        "Model class ends with 'Schema'")

                class Meta:
                    model = cls
                    model_converter = ModelConverter
                    sqla_session = self.db.session

                schema_class_name = '%sSchema' % cls.__name__

                schema_class = type(schema_class_name, (ModelSchema,), {'Meta': Meta})

                setattr(cls, '__marshmallow__', schema_class)

        logger.debug('Adding marshmallow schema to models...')
        for model in self.get_models():
            add_schema(model)
            logger.debug('\_ Model %s.' % class_name(model))

    # noinspection PyMethodMayBeStatic
    def pre_setup_models(self):
        # Add versions supporting.
        # __versioned__ = {} must be added to all models that are to be versioned.
        plugins = (
            PropertyModTrackerPlugin(),
            TransactionChangesPlugin(),
            ActivityPlugin()
        )
        make_versioned(user_cls=None, plugins=plugins)

    def post_setup_models(self):
        sa.orm.configure_mappers()

    def setup_models(self):
        self.pre_setup_models()

        logger.debug('\_ Models loading started.')
        for module in self.get_models_modules():
            importlib.import_module(module)
            logger.debug('  \_ Models from `%s` loaded.' % module)

        self.post_setup_models()

        logger.debug('\_ Installed models:')
        for model in self.get_models():
            logger.debug('  \_ Model %s.' % class_name(model))

        # self.db.create_all()
        logger.debug('All database tables created.')

        self.update_models()

    def setup(self):
        """Setup application."""
        logger.debug('Application setup started.')
        self.setup_models()
        self.setup_internal_api()
        logger.debug('Application setup finished.')

    def setup_internal_api(self):
        importlib.import_module(settings.INTERNAL_API_CONF)
        internal_api.service = self.service
        logger.debug('\_ Internal api installed.')

    @property
    @lru_cache()
    def service(self):
        """
        Returns an instance of service class ``self.service_class``.
        """
        service_class = import_string(self.service_class)
        service_instance = service_class(app=self)
        return service_instance

    def reverse_url(self, name, *args, external=False):
        """
        Returns a URL path for handler named ``name``.
        """
        url = self.service.reverse_url(name, *args)
        if external:
            return urljoin(self.settings.LOCATION, url)
        return url

    def run(self, **kwargs):
        """Run server."""
        logger.debug('Go starting server...')
        self.service.start(**kwargs)
