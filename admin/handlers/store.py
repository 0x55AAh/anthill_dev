from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import (
    StoreForm, StoreItemForm, StoreOrderForm, StoreItemCategoryForm,
    StoreCurrencyForm, StoreTierForm
)


class StorePageHandler(ServicePageHandler):
    service_name = 'store'


class StoreFormHandler(FormMixin, ProcessFormMixin, StorePageHandler):
    pass


class IndexHandler(StorePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['items_list'] = []  # TODO:
        return context


class ItemDetailHandler(StoreFormHandler):
    page_name = 'item_detail'
    form_class = StoreItemForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        item_id = self.path_kwargs['item_id']
        context['item'] = {}  # TODO:
        return context


class TierListHandler(StorePageHandler):
    page_name = 'tier_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['tiers'] = []  # TODO:
        return context


class TierDetailHandler(StoreFormHandler):
    page_name = 'tier_detail'
    form_class = StoreTierForm

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


class StoreDetailHandler(StoreFormHandler):
    page_name = 'store_detail'
    form_class = StoreForm

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


class OrderDetailHandler(StoreFormHandler):
    page_name = 'order_detail'
    form_class = StoreOrderForm

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


class ItemCategoryDetailHandler(StoreFormHandler):
    page_name = 'item_category_detail'
    form_class = StoreItemCategoryForm

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


class CurrencyDetailHandler(StoreFormHandler):
    page_name = 'currency_detail'
    form_class = StoreCurrencyForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        currency_id = self.path_kwargs['currency_id']
        context['currency'] = {}  # TODO:
        return context
