from .user import User
# Import other models here as they are created

# This line is important to ensure that SQLAlchemy can find the models
# when creating tables.
from app.core.config import Base
