from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Add more fields as needed for Chimera, e.g.:
    # api_key = Column(String, unique=True, index=True, nullable=True)
    # preferences = Column(JSON, nullable=True) # For storing user-specific agent settings
    # last_login_at = Column(DateTime(timezone=True), nullable=True)
