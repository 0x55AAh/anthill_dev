# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.conf import settings
from anthill.framework.utils.asynchronous import as_future
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy_utils.types.json import JSONType
from jsonpath_ng.ext import parser
from types import FunctionType


class Profile(InternalAPIMixin, db.Model):
    """Extra fields for User model."""
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    payload = db.Column(JSONType, nullable=False, default={})

    async def get_user(self):
        return await self.internal_request('login', 'get_user', user_id=self.user_id)

    # noinspection PyMethodMayBeStatic
    def _parse_obj(self, path: str):
        return parser.parse(path, debug=settings.DEBUG)

    @as_future
    def find_payload(self, path: str):
        return self._parse_obj(path).find(self.payload)

    @as_future
    def filter_payload(self, path: str, fn: FunctionType):
        return self._parse_obj(path).filter(fn, self.payload)

    @as_future
    def update_payload(self, path: str, data, commit=True):
        self.payload = self._parse_obj(path).update(self.payload, data)
        self.save(commit)
