# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.auth.models import (
    User as BaseUser,
    Profile as BaseProfile
)


class User(BaseUser):
    pass


class Profile(BaseProfile):
    pass
