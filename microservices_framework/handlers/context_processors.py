from microservices_framework.conf import settings
from microservices_framework.utils.module_loading import import_string
from microservices_framework.core.exceptions import ImproperlyConfigured
from tornado.web import RequestHandler
import logging

logger = logging.getLogger('app.handlers')

CONTEXT_PROCESSORS = getattr(settings, 'CONTEXT_PROCESSORS', [])


def build_context_from_context_processors(handler: RequestHandler) -> dict:
    """Build extra context for current handler on every request"""
    ctx = {}
    for ctx_processor in CONTEXT_PROCESSORS:
        f = import_string(ctx_processor)
        result = f(handler)
        if not isinstance(handler, RequestHandler):
            raise ImproperlyConfigured(
                'Context processor `%s` got `%s` object, '
                'but need `tornado.web.RequestHandler`' % (f.__name__, handler.__class__.__name__)
            )
        if not isinstance(result, dict):
            raise ImproperlyConfigured('Context processor `%s` must return dict object' % f.__name__)
        if not result:
            logging.warning('Empty result for context processor `%s`' % f.__name__)
        ctx.update(result)
    return ctx
