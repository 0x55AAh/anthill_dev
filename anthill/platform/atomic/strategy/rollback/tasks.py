from anthill.platform.atomic.exceptions import (
    TransactionTimeoutError, TransactionTaskTimeoutError)
from anthill.platform.core.celery import app as celery_app
from anthill.platform.atomic.strategy import manager, logger


@celery_app.task
def transaction_control(transaction_id):
    transaction = manager().storage.get_transaction(transaction_id)
    try:
        transaction.check_timeout()
    except TransactionTimeoutError:
        transaction.rollback()


@celery_app.task
def transaction_task_control(transaction_id, task_id):
    transaction = manager().storage.get_transaction(transaction_id)
    task = transaction.get_task(task_id)
    try:
        task.check_timeout()
    except TransactionTaskTimeoutError:
        transaction.rollback()
