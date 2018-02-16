from collections import defaultdict

from microservices_framework.conf import settings
from microservices_framework.utils.module_loading import import_string
from urllib.parse import urlparse
from _thread import get_ident
import importlib

from microservices_framework.utils.text import slugify, camel_case_to_spaces


class CommandNamesDuplicatedError(Exception):
    pass


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

        self.protocol, self.host, self.port = self._parse_location()
        self.extensions = {}
        setattr(self, '__ident_func__', get_ident)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.label)

    def _get_default(self, key, default=None):
        return getattr(self.settings, key, None) or default

    def _parse_location(self):
        location = urlparse(getattr(self.settings, 'LOCATION'))
        return location.scheme, location.hostname, location.port

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

    @property
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

    def routes(self):
        return importlib.import_module(self.routes_conf)

    def setup(self):
        importlib.import_module(self.models_conf)

    def run(self, **kwargs):
        service_class = import_string(self.service_class)
        service = service_class()
        service.start(**kwargs)
