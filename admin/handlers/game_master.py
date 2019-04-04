from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import (
    GameDeploymentForm, GameServerForm, GameRegionForm, GameVersionForm,
    GameRoomForm, GameForm, GameConfigForm
)


class GamePageHandler(ServicePageHandler):
    service_name = 'game_master'


class GameFormHandler(FormMixin, ProcessFormMixin, GamePageHandler):
    pass


class IndexHandler(GamePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['deployments_list'] = []  # TODO:
        return context


class DeploymentDetailHandler(GameFormHandler):
    page_name = 'deployment_detail'
    form_class = GameDeploymentForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        deployment_id = self.path_kwargs['deployment_id']
        context['deployment'] = {}  # TODO:
        return context


class ServerListHandler(GamePageHandler):
    page_name = 'server_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['servers_list'] = []  # TODO:
        return context


class ServerDetailHandler(GameFormHandler):
    page_name = 'server_detail'
    form_class = GameServerForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        server_id = self.path_kwargs['server_id']
        context['server'] = {}  # TODO:
        return context


class RegionListHandler(GamePageHandler):
    page_name = 'region_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['regions_list'] = []  # TODO:
        return context


class RegionDetailHandler(GameFormHandler):
    page_name = 'region_detail'
    form_class = GameRegionForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        region_id = self.path_kwargs['region_id']
        context['region'] = {}  # TODO:
        return context


class GameVersionListHandler(GamePageHandler):
    page_name = 'game_version_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['game_versions_list'] = []  # TODO:
        return context


class GameVersionDetailHandler(GameFormHandler):
    page_name = 'game_version_detail'
    form_class = GameVersionForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        game_version_id = self.path_kwargs['game_version_id']
        context['game_version'] = {}  # TODO:
        return context


class GameRoomListHandler(GamePageHandler):
    page_name = 'game_room_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['game_rooms_list'] = []  # TODO:
        return context


class GameRoomDetailHandler(GameFormHandler):
    page_name = 'game_room_detail'
    form_class = GameRoomForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        game_room_id = self.path_kwargs['game_room_id']
        context['game_room'] = {}  # TODO:
        return context


class GameListHandler(GamePageHandler):
    page_name = 'game_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['game_list'] = []  # TODO:
        return context


class GameDetailHandler(GameFormHandler):
    page_name = 'game_detail'
    form_class = GameForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        game_id = self.path_kwargs['game_id']
        context['game'] = {}  # TODO:
        return context


class GameConfigListHandler(GamePageHandler):
    page_name = 'game_config_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['game_configs_list'] = []  # TODO:
        return context


class GameConfigDetailHandler(GameFormHandler):
    page_name = 'game_config_detail'
    form_class = GameConfigForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        game_config_id = self.path_kwargs['game_config_id']
        context['game_config'] = {}  # TODO:
        return context
