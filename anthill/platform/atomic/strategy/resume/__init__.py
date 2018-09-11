from anthill.platform.atomic.strategy import BaseStrategy, logger
from typing import TypeVar
from . import tasks

Transaction = TypeVar('Transaction')


class Strategy(BaseStrategy):
    tasks_module = tasks

    async def proceed(self, transaction: Transaction) -> None:
        await transaction.resume()
