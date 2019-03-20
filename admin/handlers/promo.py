from ._base import ServicePageHandler


class PromoPageHandler(ServicePageHandler):
    service_name = 'promo'


class IndexHandler(PromoPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['promo_codes'] = []  # TODO:
        return context


class PromoCodeDetailHandler(PromoPageHandler):
    page_name = 'promo_code_detail'
