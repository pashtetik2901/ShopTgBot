from sqlalchemy import select
from bot.database.models import User
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging


class UserDAO(BaseDAO):
    model = User
    
    @classmethod
    async def add_first_user(cls, telegram_id: int, session: AsyncSession) -> User | None:
        new_user = cls.model(telegram_id=telegram_id)
        try:
            session.add(new_user)
            await session.commit()
            logging.info("Пользователь добавлен!")
            await session.refresh(new_user)
            return new_user
        except Exception as err:
            logging.error(err)
            await session.rollback()

    @classmethod
    async def get_by_telegram_id(cls, telegram_id: int,  session: AsyncSession) -> User | None:
        stmt = select(cls.model).filter_by(telegram_id=telegram_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_by_username(cls, username: str, session: AsyncSession) -> User | None:
        stmt = select(cls.model).filter(cls.model.username.ilike(username))
        result = await session.execute(stmt)
        return result.scalars().first()