from microservices_framework.conf import settings
from microservices_framework.utils.module_loading import import_string
from urllib.parse import urlparse
from _thread import get_ident


class Application:
    def __init__(self):
        self.settings = settings
        self.debug = settings.DEBUG
        self.name = settings.APPLICATION_NAME
        self.label = self.name.rpartition('.')[2]
        self.verbose_name = settings.APPLICATION_VERBOSE_NAME or self.label.title()
        self.description = settings.APPLICATION_DESCRIPTION
        self.icon_class = settings.APPLICATION_ICON_CLASS
        self.routes_conf = getattr(settings, 'ROUTES_CONF', '%s.routes' % self.name)
        self.service_class = getattr(settings, 'SERVICE_CLASS', '%s.services.Service' % self.name)
        self.protocol, self.socket = self._parse_location()
        self.registry_entry = self._build_registry_entry()
        self.commands = {}
        setattr(self, '__ident_func__', get_ident)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.label)

    def _parse_location(self):
        location = urlparse(getattr(self.settings, 'LOCATION'))
        return location.scheme, (location.hostname, location.port or 80)

    def _build_registry_entry(self):
        entry = {
            network: self.settings.LOCATION
            for network in self.settings.NETWORKS
        }
        entry.update(broker=settings.BROKER)
        return entry

    def run(self):
        service_class = import_string(self.service_class)
        service = service_class()
        service.start()
