from anthill.platform.atomic.transaction import Transaction
from anthill.framework.utils.singleton import Singleton


class TransactionManager(metaclass=Singleton):
    def __init__(self, transactions=None):
        self.transactions = transactions or []

    @property
    def _transactions_dict(self):
        return {t.id: t for t in self.transactions}

    def new_transaction(self, *args, **kwargs):
        transaction = Transaction(*args, **kwargs)
        transaction.manager = self
        self.transactions.append(transaction)
        return transaction

    def get_transaction(self, id_):
        return self._transactions_dict.get(id_)

    def size(self):
        return len(self.transactions)
