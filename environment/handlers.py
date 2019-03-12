from anthill.platform.auth.handlers import UserRequestHandler


class DiscoverHandler(UserRequestHandler):
    async def get(self, app_name, app_version):
        pass

