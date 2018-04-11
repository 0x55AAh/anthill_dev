# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
