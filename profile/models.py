# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.conf import settings
from anthill.framework.utils.asynchronous import as_future
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy_utils.types import JSONType
from jsonpath_ng.ext import parser


class Profile(InternalAPIMixin, db.Model):
    """Extra data for User model."""
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    payload = db.Column(JSONType, nullable=False, default={})
    active = db.Column(db.Boolean, nullable=False, default=True)

    async def get_user(self):
        return await self.internal_request('login', 'get_user', user_id=self.user_id)

    @staticmethod
    def _payload_parse_obj(path: str):
        return parser.parse(path, debug=settings.DEBUG)

    @as_future
    def find_payload(self, path: str):
        return self._payload_parse_obj(path).find(self.payload)

    @as_future
    def filter_payload(self, path: str, fn):
        return self._payload_parse_obj(path).filter(fn, self.payload)

    @as_future
    def update_payload(self, path: str, data, commit=True):
        self.payload = self._payload_parse_obj(path).update(self.payload, data)
        self.save(commit)
