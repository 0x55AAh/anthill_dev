from anthill.platform.atomic.transaction import (
    TransactionTimeoutError, TransactionTaskTimeoutError)
from anthill.platform.core.celery import app as celery_app
from anthill.platform.atomic.manager import TransactionManager


manager = TransactionManager()


@celery_app.task
def transaction_duration_control(transaction_id):
    transaction = manager.get_transaction(transaction_id)
    try:
        transaction.check_duration()
    except TransactionTimeoutError:
        transaction.rollback()


@celery_app.task
def transaction_task_duration_control(transaction_id, task_id):
    transaction = manager.get_transaction(transaction_id)
    task = transaction.get_task(task_id)
    try:
        task.check_duration()
    except TransactionTaskTimeoutError:
        transaction.rollback()
