"""
Global Django exception and warning classes.
"""


class FieldDoesNotExist(Exception):
    """The requested model field does not exist"""
    pass


class ObjectDoesNotExist(Exception):
    """The requested object does not exist"""
    silent_variable_failure = True


class MultipleObjectsReturned(Exception):
    """The query returned multiple objects when only one was expected."""
    pass


class SuspiciousOperation(Exception):
    """The user did something suspicious"""


class SuspiciousMultipartForm(SuspiciousOperation):
    """Suspect MIME request in multipart form data"""
    pass


class SuspiciousFileOperation(SuspiciousOperation):
    """A Suspicious filesystem operation was attempted"""
    pass


class DisallowedHost(SuspiciousOperation):
    """HTTP_HOST header contains invalid value"""
    pass


class PermissionDenied(Exception):
    """The user did not have permission to do that"""
    pass


class ImproperlyConfigured(Exception):
    """Django is somehow improperly configured"""
    pass
