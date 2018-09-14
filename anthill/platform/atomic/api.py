from anthill.platform.api.internal import as_internal, InternalAPI
from anthill.platform.atomic.manager import TransactionManager


manager = TransactionManager()


@as_internal()
async def transaction_commit(api: InternalAPI, transaction_id):
    pass


@as_internal()
async def transaction_rollback(api: InternalAPI, transaction_id):
    pass


@as_internal()
async def transaction_resume(api: InternalAPI, transaction_id):
    pass
