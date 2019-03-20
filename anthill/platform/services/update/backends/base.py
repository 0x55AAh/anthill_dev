from typing import List, Optional


class BaseBackend:
    async def versions(self) -> List[str]:
        raise NotImplementedError

    async def current_version(self) -> str:
        raise NotImplementedError

    async def check_updates(self) -> List[str]:
        raise NotImplementedError

    async def update(self, version: Optional[str] = None) -> None:
        raise NotImplementedError
