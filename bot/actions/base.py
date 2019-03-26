from abc import ABC, abstractmethod
from typing import Callable


class BaseAction(ABC):
    @abstractmethod
    async def on_message(self, data: dict, emit: Callable) -> None:
        pass
