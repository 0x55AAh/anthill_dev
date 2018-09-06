from anthill.platform.core.celery import app as celery_app


@celery_app.task
def commit_contoll(transaction_id):
    pass
