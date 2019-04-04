# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from anthill.framework.utils.urls import include, root
from admin.handlers import game_master as handlers, LogRequestHandler


@root(pattern=r'^/game/', namespace='game_master')
def route_patterns():
    return [
        url(r'^/?$', handlers.IndexHandler, name='index'),

        url(r'^/deployments/?$', handlers.IndexHandler, name='deployment_list'),
        url(r'^/deployments/(?P<deployment_id>[^/]+)/?$', handlers.DeploymentDetailHandler,
            name='deployment_detail'),

        url(r'^/servers/?$', handlers.ServerListHandler, name='server_list'),
        url(r'^/servers/(?P<server_id>[^/]+)/?$', handlers.ServerDetailHandler, name='server_detail'),

        url(r'^/regions/?$', handlers.RegionListHandler, name='region_list'),
        url(r'^/regions/(?P<region_id>[^/]+)/?$', handlers.RegionDetailHandler, name='region_detail'),

        url(r'^/game_versions/?$', handlers.GameVersionListHandler, name='game_version_list'),
        url(r'^/game_versions/(?P<game_version_id>[^/]+)/?$', handlers.GameVersionDetailHandler,
            name='game_version_detail'),

        url(r'^/game_rooms/?$', handlers.GameRoomListHandler, name='game_room_list'),
        url(r'^/game_rooms/(?P<game_room_id>[^/]+)/?$', handlers.GameRoomDetailHandler,
            name='game_room_detail'),

        url(r'^/games/?$', handlers.GameListHandler, name='game_list'),
        url(r'^/games/(?P<game_id>[^/]+)/?$', handlers.GameDetailHandler, name='game_detail'),

        url(r'^/game_configs/?$', handlers.GameConfigListHandler, name='game_config_list'),
        url(r'^/game_configs/(?P<game_config_id>[^/]+)/?$', handlers.GameConfigDetailHandler,
            name='game_config_detail'),

        url(r'^/log/?$', LogRequestHandler, {'service_name': 'game_master'}, name='log')
    ]
