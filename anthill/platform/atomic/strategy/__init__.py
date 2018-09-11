from typing import List, Dict, Callable, TypeVar
import logging

logger = logging.getLogger('anthill.application')
Transaction = TypeVar('Transaction')


class BaseStrategy:
    TRANSACTION = 'transaction'
    TRANSACTION_TASK = 'transaction_task'

    tasks_module = None

    @property
    def tasks(self) -> Dict[str, Callable]:
        return {
            self.TRANSACTION: getattr(self.tasks_module, 'transaction_control'),
            self.TRANSACTION_TASK: getattr(self.tasks_module, 'transaction_task_control')
        }

    def get_task(self, target: str) -> Callable:
        target = getattr(self, target, None)
        return self.tasks.get(target)

    async def apply_many(self, transactions: List[Transaction]):
        for transaction in transactions:
            await self.apply_one(transaction)

    async def apply_one(self, transaction: Transaction) -> bool:
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError

    def finish(self) -> None:
        raise NotImplementedError


def manager():
    from anthill.platform.atomic.manager import TransactionManager
    return TransactionManager()
