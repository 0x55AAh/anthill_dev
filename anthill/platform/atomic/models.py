from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.platform.atomic.exceptions import (
    TransactionError, TransactionTaskError, TransactionTimeoutError,
    TransactionTaskTimeoutError
)
import enum
import logging

logger = logging.getLogger('anthill.application')


@enum.unique
class Status(enum.Enum):
    NEW = 0
    STARTED = 1
    SUCCESSFUL = 2
    FAILED = 3
    ROLLBACK_STARTED = 4
    ROLLBACK_SUCCESSFUL = 5
    ROLLBACK_FAILED = 6


class BaseTransaction(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # TODO: UUID type
    started = db.Column(db.DateTime, nullable=False, default=timezone.now)
    finished = db.Column(db.DateTime)
    status = db.Column(db.Enum(Status), nullable=False, default=Status.NEW)
    timeout = db.Column(db.Integer, nullable=False, default=0)

    def is_finished(self):
        return self.finished is not None

    async def commit(self):
        pass

    async def rollback(self):
        pass


class Transaction(BaseTransaction):
    __tablename__ = 'transactions'
    __table_args__ = ()

    tasks = db.relationship(
        'TransactionTask', backref=db.backref('transaction'), lazy='dynamic',
        cascade='all, delete-orphan')
    state = db.Column(db.Integer, nullable=False, default=0)

    def check_timeout(self):
        if not self.is_finished():
            if timezone.now() - self.started > self.timeout:
                raise TransactionTimeoutError('Transaction timeout: %s' % self.timeout)

    def get_tasks(self):
        return self.tasks.all()

    def add(self, task):
        self.tasks.append(task)
        logger.info('Transaction task appended: %s' % task.id)

    def create_task(self, *args, **kwargs):
        task = TransactionTask(*args, **kwargs)
        self.tasks.append(task)
        logger.info('Transaction task created: %s' % task.id)
        return task

    def delete_task(self, id_):
        task = self.tasks.get(id_)
        self.tasks.remove(task)
        logger.info('Transaction task deleted: %s' % id_)

    def size(self):
        return self.tasks.count()

    async def commit(self):
        self.commit_start()
        for task in self.tasks:
            try:
                await task.commit()
            except TransactionError:
                self.status = Status.FAILED
                return
            else:
                self.state_incr()
        self.commit_finish()

    def state_incr(self):
        self.state += 1

    def state_decr(self):
        self.state -= 1

    def commit_start(self):
        self.status = Status.STARTED
        from anthill.platform.atomic.tasks import transaction_duration_control
        transaction_duration_control.apply_async((self.id,), countdown=self.timeout)

    def commit_finish(self):
        self.status = Status.SUCCESSFUL
        self.finished = timezone.now()

    @property
    def tasks_for_rollback(self):
        return self.get_tasks()[:self.state]

    async def rollback(self):
        self.rollback_start()
        for task in self.tasks_for_rollback:
            try:
                await task.rollback()
            except TransactionError:
                self.status = Status.ROLLBACK_FAILED
                return
            else:
                self.state_decr()
        self.rollback_finish()

    def rollback_start(self):
        self.status = Status.ROLLBACK_STARTED

    def rollback_finish(self):
        self.status = Status.ROLLBACK_SUCCESSFUL
        self.finished = timezone.now()


class TransactionTask(BaseTransaction):
    __tablename__ = 'transaction_tasks'
    __table_args__ = ()

    shared = db.Column(db.Boolean, nullable=False, default=False)
    remote = db.Column(db.Boolean, nullable=False, default=False)

    transaction_id = db.Column(
        db.Integer, db.ForeignKey('transactions.id'), nullable=False, index=True)

    def check_timeout(self):
        if not self.is_finished():
            if timezone.now() - self.started > self.timeout:
                raise TransactionTaskTimeoutError('Transaction task timeout: %s' % self.timeout)
