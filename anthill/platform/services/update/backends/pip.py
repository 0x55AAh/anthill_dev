from pip import _internal as pip_internal
from .base import BaseBackend
from typing import List, Optional
import logging


class Backend(BaseBackend):
    async def versions(self) -> List[str]:
        pass

    async def current_version(self) -> str:
        pass

    async def check_updates(self) -> List[str]:
        pass

    async def update(self, version: Optional[str] = None) -> None:
        pass
