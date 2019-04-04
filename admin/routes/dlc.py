# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import dlc as handlers, LogRequestHandler


@root(pattern=r'^/dlc/', namespace='dlc')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),
        url(r'^/bundles/?$', handlers.IndexHandler, name='bundles'),
        url(r'^/bundles/(?P<bundle_id>[^/]+)/?$', handlers.BundleDetailHandler, name='bundle_detail'),

        url(r'^/applications/?$', handlers.ApplicationListHandler, name='application_list'),
        url(r'^/applications/(?P<application_id>[^/]+)/?$', handlers.ApplicationDetailHandler,
            name='application_detail'),

        url(r'^/application_versions/?$', handlers.ApplicationVersionListHandler, name='application_version_list'),
        url(r'^/application_versions/(?P<application_version_id>[^/]+)/?$', handlers.ApplicationVersionDetailHandler,
            name='application_version_detail'),

        url(r'^/data_versions/?$', handlers.DataVersionListHandler, name='data_version_list'),
        url(r'^/data_versions/(?P<data_version_id>[^/]+)/?$', handlers.DataVersionDetailHandler,
            name='data_version_detail'),

        url(r'^/log/?$', LogRequestHandler, {'service_name': 'dlc'}, name='log')
    ]
