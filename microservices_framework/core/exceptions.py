"""
Global Django exception and warning classes.
"""


class FieldDoesNotExist(Exception):
    """The requested model field does not exist"""
    pass


class AppRegistryNotReady(Exception):
    """The django.apps registry is not populated yet"""
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


class DisallowedRedirect(SuspiciousOperation):
    """Redirect to scheme not in allowed list"""
    pass


class TooManyFieldsSent(SuspiciousOperation):
    """
    The number of fields in a GET or POST request exceeded
    settings.DATA_UPLOAD_MAX_NUMBER_FIELDS.
    """
    pass


class RequestDataTooBig(SuspiciousOperation):
    """
    The size of the request (excluding any file uploads) exceeded
    settings.DATA_UPLOAD_MAX_MEMORY_SIZE.
    """
    pass


class PermissionDenied(Exception):
    """The user did not have permission to do that"""
    pass


class ImproperlyConfigured(Exception):
    """Django is somehow improperly configured"""
    pass


class FieldError(Exception):
    """Some kind of problem with a model field."""
    pass


class EmptyResultSet(Exception):
    """A database query predicate is impossible."""
    pass
