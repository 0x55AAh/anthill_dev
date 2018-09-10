from typing import List, Dict, Callable, TypeVar

Transaction = TypeVar('Transaction')


class BaseStrategy:
    TRANSACTION = 'transaction'
    TRANSACTION_TASK = 'transaction_task'

    tasks_module = None

    @property
    def tasks(self) -> Dict[str, Callable]:
        return {
            self.TRANSACTION: getattr(tasks_module, 'transaction_control'),
            self.TRANSACTION_TASK: getattr(tasks_module, 'transaction_task_control')
        }

    async def apply_many(self, transactions: List[Transaction]):
        for transaction in transactions:
            await self.apply_one(transaction)

    async def apply_one(self, transaction: Transaction) -> bool:
        raise NotImplementedError


@property
def manager():
    from anthill.platform.atomic.manager import TransactionManager
    return TransactionManager()
