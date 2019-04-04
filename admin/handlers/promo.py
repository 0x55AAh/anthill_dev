from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import PromoCodeForm


class PromoPageHandler(ServicePageHandler):
    service_name = 'promo'


class PromoFormHandler(FormMixin, ProcessFormMixin, PromoPageHandler):
    pass


class IndexHandler(PromoPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['promo_codes_list'] = []  # TODO:
        return context


class PromoCodeDetailHandler(PromoFormHandler):
    page_name = 'promo_code_detail'
    form_class = PromoCodeForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        promo_code_id = self.path_kwargs['promo_code_id']
        context['promo_code'] = {}  # TODO:
        return context
