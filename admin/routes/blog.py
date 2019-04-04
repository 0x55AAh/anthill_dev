# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import blog as handlers, LogRequestHandler


@root(pattern=r'^/blog/', namespace='blog')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),

        url(r'^/posts/?$', handlers.IndexHandler, name='post_list'),
        url(r'^/posts/(?P<post_id>[^/]+)/?$', handlers.PostDetailHandler, name='post_detail'),

        url(r'^/categories/?$', handlers.CategoryListHandler, name='category_list'),
        url(r'^/categories/(?P<category_id>[^/]+)/?$', handlers.CategoryDetailHandler, name='category_detail'),

        url(r'^/log/?$', LogRequestHandler, {'service_name': 'blog'}, name='log')
    ]
