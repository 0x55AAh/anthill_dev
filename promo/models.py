# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from sqlalchemy.orm import validates
from sqlalchemy_utils.types.json import JSONType
from anthill.framework.utils.translation import translate as _
from anthill.framework.utils.asynchronous import as_future
from anthill.framework.utils.crypto import get_random_string
from anthill.framework.core.validators import RegexValidator


PROMO_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"
PROMO_LENGTH = 12


promo_code_validator = RegexValidator(
    regex=r'^[A-Z0-9]{12}$', message=_('Promo code is not valid'))


class PromoCode(db.Model):
    __tablename__ = 'promo_codes'

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
        return get_random_string(PROMO_LENGTH, PROMO_CHARS)

    @validates('key')
    def validate_key(self, key, value):
        promo_code_validator(value)
        return value
