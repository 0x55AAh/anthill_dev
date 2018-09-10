from anthill.platform.atomic.strategy import BaseStrategy
from typing import TypeVar
from . import tasks

Transaction = TypeVar('Transaction')


class Strategy(BaseStrategy):
    tasks_module = tasks

    async def apply_one(self, transaction: Transaction) -> bool:
        return await transaction.rollback()
