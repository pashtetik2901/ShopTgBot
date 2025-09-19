from sqlalchemy import select
from bot.database.models import User
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import logging


class UserDAO(BaseDAO):
    model = User
    
    @classmethod
    async def update_user(cls, telegram_id: int, name: str, phone: str, address: str, session: AsyncSession):
        stmt = select(cls.model).where(cls.model.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        
        if user is None:
            logging.error("Пользователь не найден")
            return
        
        user.name = name
        user.phone = phone
        user.address = address
        
        try:
            await session.commit()
            await session.refresh(user)
            logging.info("Новые данные пользователя добавлены!")
        except Exception as err:
            await session.rollback()
            logging.error(f"Ошибка, добавить данные к пользователю не удалось: {err}")
    
    @classmethod
    async def add_first_user(cls, telegram_id: int, session: AsyncSession) -> User | None:
        new_user = cls.model(telegram_id=telegram_id)
        try:
            session.add(new_user)
            await session.commit()
            logging.info("Пользователь добавлен!")
            await session.refresh(new_user)
            return new_user
        
        except IntegrityError:
            logging.warning("Такой пользователь уже есть!")
            await session.rollback()
            return True
        
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