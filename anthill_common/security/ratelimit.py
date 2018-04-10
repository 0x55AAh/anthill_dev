import logging


class RateLimitExceeded(Exception):
    ...


def key_func(action, key, level):
    return 'rate:{0}:{1}:{2}'.format(action, key, level)


class RateLimitLock:
    def __init__(self, storage, action):
        self.storage = storage
        self.action = action

    async def rollback(self):
        ...


class RateLimit:
    LEVELS = ((8, 16), (4, 8), (2, 4), (1, 1))

    def __init__(self, storage, actions):
        self.storage = storage
        self.actions = actions

    async def apply(self, action, key):
        limit = self.actions.get(action)

        if not limit:
            return

        requests_limit, time_limit = limit

        keys = [
            key_func(action, key, str(level))
            for level, _ in self.LEVELS
        ]

        # values = await self.storage.get_many(keys)
        values = []

        for value in values:
            if value is not None and int(value) <= 0:
                raise RateLimitExceeded()

        return RateLimitLock(self.storage, action)
