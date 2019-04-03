# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import store as handlers, LogRequestHandler


@root(pattern=r'^/store/', namespace='store')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),

        url(r'^/currencies/?$', handlers.CurrencyListHandler, name='currency_list'),
        url(r'^/currencies/(?P<currency_id>[^/]+)/?$', handlers.CurrencyDetailHandler, name='currency_detail'),

        url(r'^/item-categories/?$', handlers.ItemCategoryListHandler, name='item_category_list'),
        url(r'^/item-categories/(?P<item_category_id>[^/]+)/?$', handlers.ItemCategoryDetailHandler,
            name='item_category_detail'),

        url(r'^/orders/?$', handlers.OrderListHandler, name='order_list'),
        url(r'^/orders/(?P<order_id>[^/]+)/?$', handlers.OrderDetailHandler, name='order_detail'),

        url(r'^/stores/?$', handlers.StoreListHandler, name='store_list'),
        url(r'^/stores/(?P<store_id>[^/]+)/?$', handlers.StoreDetailHandler, name='store_detail'),

        url(r'^/tiers/?$', handlers.TierListHandler, name='tier_list'),
        url(r'^/tiers/(?P<tier_id>[^/]+)/?$', handlers.TierDetailHandler, name='tier_detail'),

        url(r'^/log/?$', LogRequestHandler, {'service_name': 'store'}, name='log')
    ]
