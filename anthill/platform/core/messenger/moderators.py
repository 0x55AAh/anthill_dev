from abc import ABC, abstractmethod


class ModeratedException(Exception):
    def __init__(self, decline_reason, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decline_reason = decline_reason

    def __str__(self):
        return self.decline_reason


class BaseModerator(ABC):
    @property
    @abstractmethod
    def decline_reason(self):
        pass

    @abstractmethod
    async def moderate(self, message: str) -> None:
        pass
