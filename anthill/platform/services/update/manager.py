class UpdateManager:
    schemes = ('git', 'pip', 'pip+git')

    def __init__(self, scheme='git'):
        self.scheme = scheme

    async def versions(self):
        pass

    async def current_version(self):
        pass

    async def check_updates(self):
        pass

    async def update(self, version=None):
        pass
