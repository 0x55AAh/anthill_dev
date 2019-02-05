# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from sqlalchemy_utils.types.json import JSONType
from anthill.framework.utils.asynchronous import as_future
from anthill.framework.utils.crypto import get_random_string
import re


PROMO_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"
PROMO_RE = re.compile("^[A-Z0-9]{12}$")


class Promocode(db.Model):
    __tablename__ = 'promocodes'

    key = db.Column(db.String(255), primary_key=True)
    count = db.Column(db.Integer, nullable=False, default=1)
    payload = db.Column(JSONType, nullable=False, default={})
    expires = db.Column(db.DateTime, nullable=False)

    async def save(self, *args, **kwargs):
        if not self.key:
            self.key = await self.generate_key()
        super().save(*args, **kwargs)

    @as_future
    def generate_key(self):
        return get_random_string(12, PROMO_CHARS)

    @staticmethod
    def validate_key(key):
        if not PROMO_RE.match(key):
            raise ValueError('Promo code is not valid')
