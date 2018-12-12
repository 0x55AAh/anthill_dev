from anthill.platform.services import PlainService, ControllerRole


class Service(ControllerRole, PlainService):
    """Anthill default service."""
    auto_register_on_discovery = False
