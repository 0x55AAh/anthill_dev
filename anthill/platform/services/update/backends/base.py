class BaseBackend:
    async def versions(self):
        raise NotImplementedError

    async def current_version(self):
        raise NotImplementedError

    async def check_updates(self):
        raise NotImplementedError

    async def update(self, version=None):
        raise NotImplementedError
