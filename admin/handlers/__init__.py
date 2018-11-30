from anthill.framework.handlers import RequestHandler
from anthill.platform.handlers.jsonrpc import JsonRPCSessionHandler, jsonrpc_method
from anthill.platform.auth.handlers import (
    LoginHandler as BaseLoginHandler,
    LogoutHandler as BaseLogoutHandler,
    UserTemplateHandler,
    UserHandlerMixin
)
from anthill.framework.http.errors import HttpBadRequestError
from anthill.platform.handlers.base import InternalRequestHandlerMixin
from anthill.framework.utils.decorators import authenticated
from admin.handlers._base import ServiceContextMixin, UserTemplateServiceRequestHandler
from admin.ui.modules import ServiceCard
from typing import Optional
import logging
import inspect


logger = logging.getLogger('anthill.application')


# @authenticated()
class HomeHandler(InternalRequestHandlerMixin, UserTemplateHandler):
    template_name = 'index.html'

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.metadata = []

    async def get_service_cards(self):
        self.metadata = self.settings['services_meta']
        service_cards = list(map(lambda m: ServiceCard.Entry(**m), self.metadata))
        service_cards.sort()
        return service_cards

    async def get_context_data(self, **kwargs):
        service_cards = await self.get_service_cards()
        kwargs.update(service_cards=service_cards)
        context = await super().get_context_data(**kwargs)
        return context


class LoginHandler(BaseLoginHandler):
    pass


# @authenticated()
class LogoutHandler(BaseLogoutHandler):
    handler_name = 'login'  # Redirect to


# @authenticated()
class DebugHandler(UserTemplateHandler):
    template_name = 'debug.html'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context


class DebugSessionHandler(UserHandlerMixin, JsonRPCSessionHandler):
    """Defines json-rpc methods for debugging."""

    def __init__(self, application, request, dispatcher=None, **kwargs):
        super().__init__(application, request, dispatcher, **kwargs)
        self._context = {'service': None}  # used by context-based methods

    def _set_context(self, name: str, value: Optional[str]):
        if name in self._context:
            self._context[name] = value

    @jsonrpc_method(name='help')
    def help(self):
        """Shows supported commands."""
        res = ''
        for i, f in enumerate(self.dispatcher.values(), 1):
            if f.kwargs.get('system', False):
                continue
            anno = inspect.getfullargspec(f).annotations
            res += '%s) %s (%s) => %s\n' % (
                i, f.__name__, str(anno).strip('{}'), f.__doc__)
        return res.rstrip()

    @jsonrpc_method(name='get_context')
    def get_context(self, name: str=''):
        """Get context variables."""
        if name in self._context:
            return 'Current context %s: %s' % (name, self._context[name] or '--')
        else:
            return 'No such context, (%s) available.' % ', '.join(self._context.keys())

    @jsonrpc_method(name='set_context')
    def set_context(self, name: str, value: Optional[str]):
        """Set context variable."""
        self._set_context(name, value)

    @jsonrpc_method(name='clear_context')
    def clear_context(self, name: str):
        """Clear context variable."""
        self._set_context(name, None)


# @authenticated()
class SidebarMainToggle(UserHandlerMixin, RequestHandler):
    """Save main sidebar state expanded or closed."""

    async def get(self):
        if self.is_ajax():
            expanded = self.session.get('sidebar-main-expanded', True)
            self.session['sidebar-main-expanded'] = not expanded
        else:
            raise HttpBadRequestError

    async def post(self):
        await self.get()


# @authenticated()
class ServiceRequestHandler(UserTemplateServiceRequestHandler):
    """Shows individual service index page."""
    template_name = 'index.html'


# @authenticated()
class LogRequestHandler(ServiceContextMixin, UserTemplateHandler):
    template_name = 'log.html'


# @authenticated()
class SettingsRequestHandler(UserTemplateHandler):
    template_name = 'settings.html'
