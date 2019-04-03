from ._base import ServicePageHandler


class StorePageHandler(ServicePageHandler):
    service_name = 'store'


class IndexHandler(StorePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['items_list'] = []  # TODO:
        return context


class TierListHandler(StorePageHandler):
    page_name = 'tier_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['tiers'] = []  # TODO:
        return context


class TierDetailHandler(StorePageHandler):
    page_name = 'tier_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        tier_id = self.path_kwargs['tier_id']
        context['tier'] = {}  # TODO:
        return context


class StoreListHandler(StorePageHandler):
    page_name = 'store_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['stores'] = []  # TODO:
        return context


class StoreDetailHandler(StorePageHandler):
    page_name = 'store_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        store_id = self.path_kwargs['store_id']
        context['store'] = {}  # TODO:
        return context


class OrderListHandler(StorePageHandler):
    page_name = 'order_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['orders'] = []  # TODO:
        return context


class OrderDetailHandler(StorePageHandler):
    page_name = 'order_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        order_id = self.path_kwargs['order_id']
        context['order'] = {}  # TODO:
        return context


class ItemCategoryListHandler(StorePageHandler):
    page_name = 'item_category_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['item_categories'] = []  # TODO:
        return context


class ItemCategoryDetailHandler(StorePageHandler):
    page_name = 'item_category_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        item_category_id = self.path_kwargs['item_category_id']
        context['item_category'] = {}  # TODO:
        return context


class CurrencyListHandler(StorePageHandler):
    page_name = 'currency_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['currencies'] = []  # TODO:
        return context


class CurrencyDetailHandler(StorePageHandler):
    page_name = 'currency_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        currency_id = self.path_kwargs['currency_id']
        context['currency'] = {}  # TODO:
        return context
