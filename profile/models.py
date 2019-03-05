# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.conf import settings
from anthill.framework.utils import timezone
from anthill.framework.utils.asynchronous import as_future
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types import (
    JSONType, CurrencyType, CountryType, LocaleType, EmailType)
from jsonpath_ng.ext import parser
from anthill.platform.auth import RemoteUser
from typing import Callable


class Profile(InternalAPIMixin, db.Model):
    """Extra data for User model."""
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=timezone.now)
    updated = db.Column(db.DateTime, onupdate=timezone.now)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    # currency = sa.Column(CurrencyType)
    # country = sa.Column(CountryType)
    # locale = sa.Column(LocaleType)
    # email = db.Column(EmailType)
    payload = db.Column(JSONType, nullable=False, default={})
    active = db.Column(db.Boolean, nullable=False, default=True)

    @hybrid_property
    def photo(self):
        return self.payload.get('avatar')

    @hybrid_property
    def name(self):
        return self.payload.get('name')

    @hybrid_property
    def first_name(self):
        return

    @hybrid_property
    def last_name(self):
        return

    @hybrid_property
    def email(self):
        return self.payload.get('email')

    @hybrid_property
    def currency(self):
        return self.payload.get('currency')

    @hybrid_property
    def country(self):
        return self.payload.get('country')

    @hybrid_property
    def language(self):
        return self.payload.get('language')

    async def get_user(self) -> RemoteUser:
        return await self.internal_request('login', 'get_user', user_id=self.user_id)

    @staticmethod
    def _payload_parse_obj(path: str):
        return parser.parse(path, debug=settings.DEBUG)

    @as_future
    def find_payload(self, path: str) -> dict:
        return self._payload_parse_obj(path).find(self.payload)

    @as_future
    def filter_payload(self, path: str, fn: Callable[[dict], bool]) -> dict:
        return self._payload_parse_obj(path).filter(fn, self.payload)

    @as_future
    def update_payload(self, path: str, data: dict, commit: bool = True) -> dict:
        self.payload = self._payload_parse_obj(path).update(self.payload, data)
        self.save(commit)
        return self.payload
