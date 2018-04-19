from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string
from anthill.framework.core.exceptions import ImproperlyConfigured
from tornado.httputil import HTTPServerRequest
import logging
import inspect

logger = logging.getLogger('anthill.handlers')

CONTEXT_PROCESSORS = getattr(settings, 'CONTEXT_PROCESSORS', [])


async def build_context_from_context_processors(request: HTTPServerRequest) -> dict:
    """Build extra context for current handler on every request"""
    ctx = {}
    for ctx_processor in CONTEXT_PROCESSORS:
        f = import_string(ctx_processor)
        # Context processor can be either co routine or plain function
        result = await f(request) if inspect.iscoroutinefunction(f) else f(request)
        if not isinstance(request, HTTPServerRequest):
            raise ImproperlyConfigured(
                'Context processor `%s` got `%s` object, '
                'but need `HTTPServerRequest`' % (f.__name__, request.__class__.__name__)
            )
        if not isinstance(result, dict):
            raise ImproperlyConfigured('Context processor `%s` must return dict object' % f.__name__)
        if not result:
            logging.warning('Empty result for context processor `%s`' % f.__name__)
        ctx.update(result)
    return ctx


def datetime(request):
    from anthill.framework.utils import timezone
    return {
        'now': timezone.now()
    }
