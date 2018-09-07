from anthill.framework.db import db
from anthill.framework.utils import timezone


class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # TODO: UUID type
    started = db.Column(db.DateTime, nullable=False, default=timezone.now)
    finished = db.Column(db.DateTime)
