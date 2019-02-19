"""
Example:
    from exec.api.session import session_api

    @session_api()
    def api_method(*args, **kwargs):
        ...
"""
from v8py import new, Context
import functools
import collections
import traceback
import weakref
import inspect
import asyncio


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

    exc = f.exception()
    if exc:
        exc.stack = ''.join(traceback.format_tb(f.exc_info()[2]))
        f.bound_reject(exc)
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
        coroutine_object = bound.method(*bound.args, handler=handler)
        f = asyncio.ensure_future(coroutine_object)
    except BaseException as exc:
        exc.stack = traceback.format_exc()
        reject(exc)
    else:
        f.bound = bound
        f.bound_resolve = resolve
        f.bound_reject = reject
        f.add_done_callback(promise_completion)


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


class SessionAPIModule:
    pass


class SessionAPI:
    _module = collections.defaultdict(SessionAPIModule)
    _methods = []

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key):
        return dict(self.items)[key]

    def __repr__(self):
        return repr(self.items)

    def __len__(self):
        return len(self.items)

    @property
    def items(self):
        return list(self._module.items()) + self._methods

    # noinspection PyMethodMayBeStatic
    def expose(self, context: Context) -> None:
        context.expose_readonly(**dict(self.items))

    def add_method(self, method, direct=False) -> None:
        if direct:
            self._methods.append([method.__name__, method])
        else:
            method_module = method.__module__.partition('.')[-1]
            setattr(self._module[method_module], method.__name__, method)

    def __call__(self, direct=False):
        """Decorator marks function as an session api method."""
        def decorator(func):
            if inspect.iscoroutinefunction(func):
                @promise
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)
            else:
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
            wrapper = functools.wraps(func)(wrapper)
            self.add_method(wrapper, direct)
            return wrapper
        return decorator


session_api = SessionAPI()
