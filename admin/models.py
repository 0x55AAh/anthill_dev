# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.auth.models import User

u = User(username='Vlad2')
# u.save()


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
