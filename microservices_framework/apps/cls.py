from collections import defaultdict
from microservices_framework.utils.text import slugify, camel_case_to_spaces
from microservices_framework.conf import settings
from microservices_framework.utils.module_loading import import_string
from urllib.parse import urlparse, urljoin
from functools import lru_cache
from _thread import get_ident
import importlib


class CommandNamesDuplicatedError(Exception):
    ...


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

        self.routes_conf = self._get_default('ROUTES_CONF', '%s.routes' % self.name)
        self.service_class = self._get_default('SERVICE_CLASS', '%s.services.Service' % self.name)
        self.management_conf = self._get_default('MANAGEMENT_CONF', '%s.management' % self.name)
        self.models_conf = self._get_default('MODELS_CONF', '%s.models' % self.name)
        self.ui_module = self._get_default('UI_MODULE', '%s.ui' % self.name)

        self.protocol, self.host, self.port = self.split_location()
        self.extensions = {}

        setattr(self, '__ident_func__', get_ident)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.label)

    def _get_default(self, key, default=None):
        return getattr(self.settings, key, None) or default

    def split_location(self):
        loc = urlparse(getattr(self.settings, 'LOCATION'))
        return loc.scheme, loc.hostname, loc.port

    @property
    @lru_cache()
    def version(self):
        mod = importlib.import_module(self.name)
        return getattr(mod, 'version', None)

    @property
    @lru_cache()
    def registry_entry(self):
        entry = {
            network: self.settings.LOCATION
            for network in self.settings.NETWORKS
        }
        entry.update(broker=settings.BROKER)
        return entry

    def get_extension(self, name):
        """Returns an extension by name or raise an exception"""
        if name not in self.extensions:
            raise ApplicationExtensionNotRegistered(name)
        return self.extensions[name]

    # noinspection PyBroadException,PyProtectedMember,SpellCheckingInspection
    def get_models(self):
        ext = self.get_extension('sqlalchemy')
        classes, models, table_names = [], [], []
        for clazz in ext.db.Model._decl_class_registry.values():
            try:
                table_names.append(clazz.__tablename__)
                classes.append(clazz)
            except Exception:
                ...
        for table in ext.db.metadata.tables.items():
            if table[0] in table_names:
                models.append(classes[table_names.index(table[0])])
        return models

    # noinspection PyProtectedMember,SpellCheckingInspection
    def get_model(self, name):
        ext = self.get_extension('sqlalchemy')
        return ext.db.Model._decl_class_registry.get(name, None)

    # noinspection PyProtectedMember,SpellCheckingInspection
    def get_model_by_tablename(self, tablename):
        ext = self.get_extension('sqlalchemy')
        for clazz in ext.db.Model._decl_class_registry.values():
            if hasattr(clazz, '__tablename__') and clazz.__tablename__ == tablename:
                return clazz

    @property
    @lru_cache()
    def commands(self):
        def is_command_class(cls):
            from microservices_framework.core.management.commands import Command
            base_classes = (Command,)
            try:
                return issubclass(cls, base_classes) and cls not in base_classes
            except TypeError:
                return False

        def is_manager_instance(obj):
            from microservices_framework.core.management import Manager
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
        """Returns routes map"""
        routes_mod = importlib.import_module(self.routes_conf)
        return getattr(routes_mod, 'route_patterns', [])

    @property
    @lru_cache()
    def ui_modules(self):
        """
        Returns module object with UIModule subclasses and plain functions.
        Use for ``service.ui_modules`` and ``service.ui_methods`` initialising.
        """
        return importlib.import_module('%s.modules' % self.ui_module)

    def setup(self):
        """Setup application"""
        importlib.import_module(self.models_conf)

    @property
    @lru_cache()
    def service(self):
        """Returns an instance of service class ``self.service_class``"""
        service_class = import_string(self.service_class)
        service_instance = service_class()
        return service_instance

    def reverse_url(self, name, *args, external=False):
        """Returns a URL path for handler named ``name``"""
        url = self.service.reverse_url(name, *args)
        if external:
            return urljoin(self.settings.LOCATION, url)
        return url

    # noinspection PyProtectedMember
    def resolve_url(self, path):
        """Returns a route attributes dict for path ``path``"""
        from tornado.web import url
        from tornado.routing import _unquote_or_none
        for r in self.routes:
            if isinstance(r, (list, tuple)):
                r = url(*r)
            if isinstance(r, url):
                match = r.regex.match(path)
                if match is not None:
                    path_args, path_kwargs = [], {}
                    # Pass matched groups to the handler. Since
                    # match.groups() includes both named and
                    # unnamed groups, we want to use either groups
                    # or groupdict but not both.
                    if r.regex.groupindex:
                        path_kwargs = dict(
                            (str(k), _unquote_or_none(v))
                            for (k, v) in match.groupdict().items())
                    else:
                        path_args = [_unquote_or_none(s) for s in match.groups()]

                    return dict(
                        name=r.name,
                        handler=r.target,
                        args=path_args,
                        kwargs=path_kwargs
                    )

    def run(self, **kwargs):
        """Run server"""
        self.service.start(**kwargs)
