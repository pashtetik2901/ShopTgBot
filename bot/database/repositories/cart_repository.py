from sqlalchemy import select
from bot.database.models import Carts, User
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class CartDAO(BaseDAO):
    model = Carts
    model_user = User
    
    @classmethod
    async def create_cart(cls, user_id: int, session: AsyncSession):
        stmt = select(cls.model_user).where(cls.model_user.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            try:
                user.carts = cls.model()
                logging.info("Корзина для пользователя создана")
                await session.commit()
            except Exception as err:
                logging.error(f"Ошибка с созданием корзины: {err}")
                await session.rollback()
        else:
            logging.error("Пользователь не найден, ошибка")