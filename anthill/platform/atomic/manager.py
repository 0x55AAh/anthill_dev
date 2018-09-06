from anthill.platform.core.atomic.transaction import Transaction


class Manager:
    def __init__(self, transactions):
        self.transactions = transactions or []

    @property
    def transactions_dict(self):
        return {t.id: t for t in self.transactions}

    def new_transaction(self, *args, **kwargs):
        transaction = Transaction(*args, **kwargs)
        transaction.manager = self
        self.transactions.append(transaction)
        return transaction

    def get_gransaction(self, id_):
        return self.transactions_dict.get(id_)
