from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.framework.utils.translation import translate as _
from sqlalchemy_utils.types import ChoiceType
from celery import schedules
import datetime


class ValidationError(Exception):
    pass


class IntervalSchedule(db.Model):
    __tablename__ = "interval_schedule"

    PERIOD_CHOICES = (
        ('days', _('Days')),
        ('hours', _('Hours')),
        ('minutes', _('Minutes')),
        ('seconds', _('Seconds')),
        ('microseconds', _('Microseconds'))
    )

    every = db.Column(db.Integer, nullable=False)
    period = db.Column(ChoiceType(PERIOD_CHOICES))
    periodic_tasks = db.relationship('PeriodicTask')

    @property
    def schedule(self):
        return schedules.schedule(datetime.timedelta(**{self.period.code: self.every}))

    @classmethod
    def from_schedule(cls, session, schedule, period='seconds'):
        every = max(schedule.run_every.total_seconds(), 0)
        obj = cls.filter_by(session, every=every, period=period).first()  # TODO: filter_by
        if obj is None:
            return cls(every=every, period=period)
        else:
            return obj

    def __str__(self):
        if self.every == 1:
            return _('every {0.period_singular}').format(self)
        return _('every {0.every} {0.period}').format(self)

    @property
    def period_singular(self):
        return self.period[:-1]


class CrontabSchedule(db.Model):
    """
    Task result/status.
    """
    __tablename__ = "crontab_schedule"

    minute = db.Column(db.String(length=120), default="*")
    hour = db.Column(db.String(length=120), default="*")
    day_of_week = db.Column(db.String(length=120), default="*")
    day_of_month = db.Column(db.String(length=120), default="*")
    month_of_year = db.Column(db.String(length=120), default="*")
    periodic_tasks = db.relationship('PeriodicTask')

    def __str__(self):
        rfield = lambda f: f and str(f).replace(' ', '') or '*'
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY)'.format(
            rfield(self.minute), rfield(self.hour), rfield(self.day_of_week),
            rfield(self.day_of_month), rfield(self.month_of_year),
        )

    @property
    def schedule(self):
        spec = {
            'minute': self.minute,
            'hour': self.hour,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
            'month_of_year': self.month_of_year
        }
        return schedules.crontab(**spec)

    @classmethod
    def from_schedule(cls, session, schedule):
        spec = {
            'minute': schedule._orig_minute,
            'hour': schedule._orig_hour,
            'day_of_week': schedule._orig_day_of_week,
            'day_of_month': schedule._orig_day_of_month,
            'month_of_year': schedule._orig_month_of_year
        }
        obj = cls.filter_by(session, **spec).first()  # TODO: filter_by
        if obj is None:
            return cls(**spec)
        else:
            return obj


class PeriodicTasks(db.Model):
    __tablename__ = "periodic_tasks"

    ident = db.Column(db.Integer, default=1, primary_key=True)
    last_update = db.Column(db.DateTime, default=timezone.now)

    @classmethod
    def changed(cls, session, instance):
        if not instance.no_changes:
            obj, _ = cls.update_or_create(  # TODO: update_or_create
                session, defaults={'last_update': timezone.now()}, ident=1)
            session.add(obj)

    @classmethod
    def last_change(cls, session):
        obj = cls.filter_by(session, ident=1).first()  # TODO: filter_by
        return obj.last_update if obj else None


class PeriodicTask(db.Model):
    __tablename__ = "periodic_task"

    name = db.Column(db.String(length=120), unique=True)
    task = db.Column(db.String(length=120))
    crontab_id = db.Column(db.Integer, db.ForeignKey('crontab_schedule.id'))
    crontab = db.relationship("CrontabSchedule", back_populates="periodic_tasks")
    interval_id = db.Column(db.Integer, db.ForeignKey('interval_schedule.id'))
    interval = db.relationship("IntervalSchedule", back_populates="periodic_tasks")
    args = db.Column(db.String(length=120))
    kwargs = db.Column(db.String(length=120))
    last_run_at = db.Column(db.DateTime, default=timezone.now)
    total_run_count = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)
    no_changes = False

    def __str__(self):
        fmt = '{0.name}: {0.crontab}'
        return fmt.format(self)

    @property
    def schedule(self):
        if self.crontab:
            return self.crontab.schedule
        if self.interval:
            return self.interval.schedule
