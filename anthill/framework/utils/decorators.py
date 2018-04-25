from functools import update_wrapper
from tornado.web import (
    url, RedirectHandler, RequestHandler, authenticated
)


class classonlymethod(classmethod):
    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError("This method is available only on the class, not on instances.")
        return super().__get__(instance, cls)


def method_decorator(decorator, name=''):
    """
    Convert a function decorator into a method decorator
    """
    # 'obj' can be a class or a function. If 'obj' is a function at the time it
    # is passed to _dec,  it will eventually be a method of the class it is
    # defined on. If 'obj' is a class, the 'name' is required to be the name
    # of the method that will be decorated.
    def _dec(obj):
        is_class = isinstance(obj, type)
        if is_class:
            if name and hasattr(obj, name):
                func = getattr(obj, name)
                if not callable(func):
                    raise TypeError(
                        "Cannot decorate '{0}' as it isn't a callable "
                        "attribute of {1} ({2})".format(name, obj, func)
                    )
            else:
                raise ValueError(
                    "The keyword argument `name` must be the name of a method "
                    "of the decorated class: {0}. Got '{1}' instead".format(
                        obj, name,
                    )
                )
        else:
            func = obj

        def decorate(function):
            """
            Apply a list/tuple of decorators if decorator is one. Decorator
            functions are applied so that the call order is the same as the
            order in which they appear in the iterable.
            """
            if hasattr(decorator, '__iter__'):
                for dec in decorator[::-1]:
                    function = dec(function)
                return function
            return decorator(function)

        def _wrapper(self, *args, **kwargs):
            @decorate
            def bound_func(*args2, **kwargs2):
                return func.__get__(self, type(self))(*args2, **kwargs2)
            # bound_func has the signature that 'decorator' expects i.e. no
            # 'self' argument, but it is a closure over self so it can call
            # 'func' correctly.
            return bound_func(*args, **kwargs)
        # In case 'decorator' adds attributes to the function it decorates, we
        # want to copy those. We don't have access to bound_func in this scope,
        # but we can cheat by using it on a dummy function.

        @decorate
        def dummy(*args, **kwargs):
            pass
        update_wrapper(_wrapper, dummy)
        # Need to preserve any existing attributes of 'func', including the name.
        update_wrapper(_wrapper, func)

        if is_class:
            setattr(obj, name, _wrapper)
            return obj

        return _wrapper
    # Don't worry about making _dec look similar to a list/tuple as it's rather
    # meaningless.
    if not hasattr(decorator, '__iter__'):
        update_wrapper(_dec, decorator)
    # Change the name to aid debugging.
    if hasattr(decorator, '__name__'):
        _dec.__name__ = 'method_decorator(%s)' % decorator.__name__
    else:
        _dec.__name__ = 'method_decorator(%s)' % decorator.__class__.__name__
    return _dec


class Route:
    """
    Decorates RequestHandlers and builds up a list of routables handlers
    Tech Notes (or "What the *@# is really happening here?")
    --------------------------------------------------------
    Everytime @route('...') is called, we instantiate a new route object which
    saves off the passed in URI. Then, since it's a decorator, the function is
    passed to the route.__call__ method as an argument. We save a reference to
    that handler with our uri in our class level routes list then return that
    class to be instantiated as normal.
    Later, we can call the classmethod route.get_routes to return that list of
    tuples which can be handed directly to the tornado.web.Application
    instantiation.

    Example:

    @route('/some/path')
    class SomeRequestHandler(RequestHandler):
        def get(self):
            goto = self.reverse_url('other')
            self.redirect(goto)

    # so you can do myapp.reverse_url('other')

    @route('/some/other/path', name='other')
    class SomeOtherRequestHandler(RequestHandler):
        def get(self):
            goto = self.reverse_url('SomeRequestHandler')
            self.redirect(goto)

    # for passing uri parameters

    @route(r'/some/(?P<parameterized>\w+)/path')
    class SomeParameterizedRequestHandler(RequestHandler):
        def get(self, parameterized):
            goto = self.reverse_url(parameterized)
            self.redirect(goto)

    my_routes = route.get_routes()
    """
    _routes = []

    def __init__(self, uri, name=None):
        self._uri = uri
        self.name = name

    def __call__(self, _handler):
        """Gets called when we class decorate"""
        name = self.name or _handler.__name__
        self._routes.append(url(self._uri, _handler, name=name))
        return _handler

    @classmethod
    def get_routes(cls):
        return cls._routes


route = Route


def route_redirect(from_, to, name=None):
    """
    route_redirect provided by Peter Bengtsson via the Tornado mailing list
    and then improved by Ben Darnell.
    Use it as follows to redirect other paths into your decorated handler.

    Example:

    from anthill.framework.utils.decorators import route, route_redirect

    route_redirect('/smartphone$', '/smartphone/')
    route_redirect('/iphone/$', '/smartphone/iphone/', name='iphone_shortcut')
    @route('/smartphone/$')
    class SmartphoneHandler(RequestHandler):
       def get(self):
           ...
    """
    route.get_routes().append(
        url(from_, RedirectHandler, dict(url=to), name=name))


def generic_route(uri, template, handler=None):
    """Maps a template to a route."""
    h_ = handler or RequestHandler

    @route(uri, name=uri)
    class GenericHandler(h_):
        _template = template

        def get(self):
            return self.render(self._template)

    return GenericHandler


def auth_generic_route(uri, template, handler):
    """
    Provides authenticated mapping of template render to route.
    :param: uri: the route path
    :param: template: the template path to render
    :param: handler: a subclass of tornado.web.RequestHandler that provides all
            the necessary methods for resolving current_user
    """
    @route(uri, name=uri)
    class AuthHandler(handler):
        _template = template

        @authenticated
        def get(self):
            return self.render(self._template)

    return AuthHandler
