from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import (
    EventForm, EventParticipantForm, EventCategoryForm, EventGeneratorForm,
    EventGeneratorPoolForm
)


class EventPageHandler(ServicePageHandler):
    service_name = 'event'


class EventFormHandler(FormMixin, ProcessFormMixin, EventPageHandler):
    pass


class IndexHandler(EventPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['events_list'] = []  # TODO:
        return context


class EventDetailHandler(EventFormHandler):
    page_name = 'event_detail'
    form_class = EventForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        event_id = self.path_kwargs['event_id']
        context['event'] = {}  # TODO:
        return context


class ParticipantListHandler(EventPageHandler):
    page_name = 'event_participant_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        event_id = self.path_kwargs['event_id']
        context['event'] = {}  # TODO:
        context['participants_list'] = []  # TODO:
        return context


class ParticipantDetailHandler(EventFormHandler):
    page_name = 'event_participant_detail'
    form_class = EventParticipantForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        event_id = self.path_kwargs['event_id']
        user_id = self.path_kwargs['user_id']
        context['participation'] = {}  # TODO:
        return context


class CategoryListHandler(EventPageHandler):
    page_name = 'event_category_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['categories_list'] = []  # TODO:
        return context


class CategoryDetailHandler(EventFormHandler):
    page_name = 'event_category_detail'
    form_class = EventCategoryForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        category_id = self.path_kwargs['category_id']
        context['category'] = {}  # TODO:
        return context


class GeneratorListHandler(EventPageHandler):
    page_name = 'generator_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['generators_list'] = []  # TODO:
        return context


class GeneratorDetailHandler(EventFormHandler):
    page_name = 'generator_detail'
    form_class = EventGeneratorForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        generator_id = self.path_kwargs['generator_id']
        context['generator'] = {}  # TODO:
        return context


class GeneratorPoolListHandler(EventPageHandler):
    page_name = 'generator_pool_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['generator_pools_list'] = []  # TODO:
        return context


class GeneratorPoolDetailHandler(EventFormHandler):
    page_name = 'generator_pool_detail'
    form_class = EventGeneratorPoolForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        generator_pool_id = self.path_kwargs['generator_pool_id']
        context['generator_pool'] = {}  # TODO:
        return context
