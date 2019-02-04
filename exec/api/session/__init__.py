"""
Example:
    from exec.api.session import session_api

    @session_api()
    def api_method(*args, **kwargs):
        ...
"""
from tornado.ioloop import IOLoop
from v8py import new, Context
from typing import Coroutine
import inspect
import functools
import collections
import traceback
import weakref


__all__ = ['session_api', 'SessionAPIError']


class SessionAPIError(Exception):
    pass


class PromiseContext:
    current = None


class BoundPromise:
    def __init__(self, handler, method, args):
        self.handler = weakref.ref(handler)
        self.method = method
        self.args = args


def promise_completion(f):
    handler = f.bound.handler()

    if handler is None:
        return

    # once the future done, set the handler to ours
    PromiseContext.current = handler

    exception = f.exception()
    if exception:
        exception.stack = "".join(traceback.format_tb(f.exc_info()[2]))
        f.bound_reject(exception)
    else:
        f.bound_resolve(f.result())

    # reset it back
    PromiseContext.current = None

    del f.bound
    del f.bound_reject
    del f.bound_resolve
    del f


def promise_callback(bound, resolve, reject):
    handler = bound.handler()

    if handler is None:
        return

    try:
        future = coroutine(bound.method)(*bound.args, handler=handler)
    except BaseException as exc:
        exc.stack = traceback.format_exc()
        reject(exc)
    else:
        future.bound = bound
        future.bound_resolve = resolve
        future.bound_reject = reject
        IOLoop.current().add_future(future, promise_completion)


def promise(method):
    """
    Decorator allows method to be used in async/await.
    Use it to call a method asynchronously from javascript.
    Example:

        @promise
        async def sum(a, b):
            await sleep(1)
            return a + b

    When called from javascript, a Promise object is returned.
    Example:

        async function test() {
            var result = await sum(5, 10);
            // using result
        }
    """
    def wrapper(*args, **kwargs):
        # Retrieve handler from PromiseContext.
        # Every javascript call has to set one
        handler = PromiseContext.current
        context = handler.context
        return new(handler.promise_type,
                   context.bind(promise_callback, BoundPromise(handler, method, args)))
    return wrapper


class SessionAPICategory:
    pass


class SessionAPI:
    categories = collections.defaultdict(SessionAPICategory)

    def __iter__(self):
        return iter(self.categories)

    def __getitem__(self, key):
        return self.categories[key]

    def __repr__(self):
        return repr(self.categories)

    def __len__(self):
        return len(self.categories)

    # noinspection PyMethodMayBeStatic
    def expose(self, context: Context) -> None:
        context.expose_readonly(**self.categories)

    def add_method(self, method) -> None:
        method_module = method.__module__.partition('.')[-1]
        setattr(self.categories[method_module], method.__name__, method)

    def __call__(self):
        """Decorator marks function as an session api method."""
        def decorator(func):
            @functools.wraps(func)
            @promise
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            self.add_method(wrapper)
            return wrapper
        return decorator


session_api = SessionAPI()
