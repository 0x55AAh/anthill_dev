from anthill.platform.api.internal import as_internal, InternalAPI
from anthill.platform.atomic.manager import TransactionManager


manager = TransactionManager()


async def _get_transaction(id_):
    return await manager.storage.get_transaction(id_)


@as_internal()
async def transaction_commit(api: InternalAPI, transaction_id):
    transaction = await _get_transaction(transaction_id)
    await transaction.commit()


@as_internal()
async def transaction_rollback(api: InternalAPI, transaction_id):
    transaction = await _get_transaction(transaction_id)
    await transaction.rollback()


@as_internal()
async def transaction_resume(api: InternalAPI, transaction_id):
    transaction = await _get_transaction(transaction_id)
    await transaction.resume()


@as_internal()
async def get_transaction(api: InternalAPI, transaction_id):
    transaction = await _get_transaction(transaction_id)
    return {'data': transaction.dump().data}


@as_internal()
async def get_transaction_task(api: InternalAPI, transaction_id, transaction_task_id):
    transaction = await _get_transaction(transaction_id)
    task = transaction.tasks.get(transaction_task_id)
    return {'data': task.dump().data}
