from sqlalchemy import select
from bot.database.models import Carts, User
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class CartDAO(BaseDAO):
    model = Carts
    model_user = User
    
    @classmethod
    async def clear_user_cart(cls, user_id: int, session: AsyncSession) -> bool:
        """Очистить корзину пользователя"""
        try:
            stmt = select(cls.model).where(cls.model.user_id == user_id)
            result = await session.execute(stmt)
            cart = result.scalars().first()
            
            if cart:
                # Удаляем все элементы корзины
                for item in cart.items:
                    await session.delete(item)
                await session.commit()
                logging.info(f"Корзина пользователя {user_id} очищена")
                return True
            return False
            
        except Exception as err:
            logging.error(f"Ошибка при очистке корзины: {err}")
            await session.rollback()
            return False
    
    @classmethod
    async def create_cart(cls, user_id: int, session: AsyncSession):
        stmt = select(cls.model_user).where(cls.model_user.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            try:
                new_cart = cls.model()
                user.carts = new_cart
                await session.commit()
                await session.refresh(new_cart)
                logging.info("Корзина для пользователя создана")
                return new_cart
            except Exception as err:
                logging.error(f"Ошибка с созданием корзины: {err}")
                await session.rollback()
        else:
            logging.error("Пользователь не найден, ошибка")
            
    @classmethod
    async def get_or_create_cart(cls, user_id: int, session: AsyncSession):
        """Получить или создать корзину для пользователя"""
        try:
            stmt = select(cls.model).where(cls.model.user_id == user_id)
            result = await session.execute(stmt)
            cart = result.scalars().first()
            
            if not cart:
                # Создаем новую корзину
                cart = cls.model(user_id=user_id)
                session.add(cart)
                await session.commit()
                await session.refresh(cart)
                logging.info(f"Создана новая корзина для пользователя {user_id}")
            
            return cart
            
        except Exception as err:
            logging.error(f"Ошибка при получении/создании корзины: {err}")
            await session.rollback()
            return None