from typing import List


class BaseBackend:
    async def versions(self) -> List[str]:
        raise NotImplementedError

    async def current_version(self) -> str:
        raise NotImplementedError

    async def check_updates(self) -> List[str]:
        raise NotImplementedError

    async def update(self, version: str = None) -> None:
        raise NotImplementedError
