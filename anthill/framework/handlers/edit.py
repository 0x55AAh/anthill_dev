from anthill.framework.handlers.base import ContextMixin, RequestHandler, TemplateMixin
from anthill.framework.core.exceptions import ImproperlyConfigured


class FormMixin(ContextMixin):
    """Provide a way to show and handle a form in a request."""
    initial = {}
    form_class = None
    success_url = None
    prefix = None

    def get_initial(self):
        """Return the initial data to use for forms on this handler."""
        return self.initial.copy()

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.prefix or ''

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this handler."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'data': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update(formdata=dict(self.request.arguments, **self.request.files))
        return kwargs

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)  # success_url may be lazy

    async def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        self.redirect(self.get_success_url())

    async def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        self.render(await self.get_context_data(form=form))

    async def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return await super().get_context_data(**kwargs)


class ProcessFormHandler(RequestHandler):
    """Render a form on GET and processes it on POST."""

    async def get(self, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        context = await self.get_context_data(**kwargs)
        self.render(**context)

    async def post(self, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.validate():
            await self.form_valid(form)
        else:
            await self.form_invalid(form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    async def put(self, *args, **kwargs):
        await self.post(*args, **kwargs)


class BaseFormHandler(FormMixin, ProcessFormHandler):
    """A base handler for displaying a form."""


class FormHandler(TemplateMixin, BaseFormHandler):
    """A handler for displaying a form and rendering a template response."""
