from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from bot.database.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id})>"

