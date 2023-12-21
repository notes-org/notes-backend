# Import all the models, so that DeclarativeBase has them before being
# imported by Alembic
from app.db.declarative_base import DeclarativeBase
from app.models import *
