from anthill.platform.atomic.strategy import BaseStrategy, logger
from typing import TypeVar
from . import tasks

Transaction = TypeVar('Transaction')


class Strategy(BaseStrategy):
    tasks_module = tasks

    def __init__(self):
        super().__init__()

    async def apply_one(self, transaction: Transaction) -> bool:
        return await transaction.resume()

    def start(self) -> None:
        pass

    def finish(self) -> None:
        pass
