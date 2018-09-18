# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from admin import handlers


route_patterns = [
    url(r'^/?$', handlers.HomeHandler, name='index'),
    url(r'^/login/?$', handlers.LoginHandler, name='login'),
    url(r'^/logout/?$', handlers.LogoutHandler, name='logout'),
    url(r'^/debug/?$', handlers.DebugHandler, name='debug'),
    url(r'^/sidebar-main-toggle/?$', handlers.SidebarMainToggle, name='sidebar-main-toggle'),
]

route_patterns += [
    url(r'^/chat/?$', handlers.TestMessengerHandler, name='chat'),  # Test
    url(r'^/json-rpc/?$', handlers.TestWSJSONRPCHandler, name='json-rpc'),  # Test
    url(r'^/upload/?$', handlers.UploadFileStreamHandler,
        dict(template_name='upload_form.html'), name='upload'),  # Test
]
