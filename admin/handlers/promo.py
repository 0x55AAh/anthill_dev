from ._base import ServicePageHandler


class PromoCodeList(ServicePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['promo_codes'] = []  # TODO:
        return context


class PromoCodeDetail(ServicePageHandler):
    page_name = 'promo_code_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context
