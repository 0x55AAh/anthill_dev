from microservices_framework.apps.builder import app
from .sqlalchemy import SQLAlchemy
from .management import Migrate

db = SQLAlchemy(app)
migrate = Migrate(app, db)
