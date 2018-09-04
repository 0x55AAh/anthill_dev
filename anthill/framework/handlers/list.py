from anthill.framework.handlers.base import (
    ContextMixin, TemplateMixin, RequestHandler)
from anthill.framework.core.paginator import Paginator


class MultipleObjectMixin(ContextMixin):
    """A mixin for handlers manipulating multiple objects."""
    allow_empty = True
    queryset = None
    model = None
    paginate_by = None
    paginate_orphans = 0
    context_object_name = None
    paginator_class = Paginator
    page_kwarg = 'page'
    ordering = None


class BaseListHandler(MultipleObjectMixin, RequestHandler):
    """A base handler for displaying a list of objects."""


class MultipleObjectTemplateMixin(TemplateMixin):
    """Mixin for responding with a template and list of objects."""
    template_name_suffix = '_list'


class ListHandler(MultipleObjectTemplateMixin, BaseListHandler):
    """
    Render some list of objects, set by `self.model` or `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    """
