from sqlalchemy import select, delete
from typing import Any
from bot.database.models import Products, Order, User
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class OrderDAO(BaseDAO):
    model = Order
    model_user = User
    
    @classmethod
    async def update_status(cls, order_id: int, new_status: str, session: AsyncSession):
        stmt = select(cls.model).where(cls.model.id == order_id)
        result = await session.execute(stmt)
        order = result.scalars().first()
        if order is None:
            logging.error("Ошибка, заказ не найден")
            return
        order.status = new_status
        try:
            await session.commit()
            await session.refresh(order)
            logging.info("Статус успешно изменен")
        except Exception as err:
            await session.rollback()
            logging.error("Ошибка изменения статуса")
    
    @classmethod
    async def get_all_order(cls, session: AsyncSession) -> list[Order]:
        stmt = select(cls.model)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def create_order(cls, user_id: int, uid: str, delivery_method: str, status: str, total_price: float, session: AsyncSession):
        stmt = select(cls.model_user).where(cls.model_user.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        
        if user is None:
            logging.info("Пользователь не найден!")
            return
        
        new_order = cls.model(
            uid=uid,
            delivery_method=delivery_method,
            status=status,
            total_price=total_price
        )
        
        user.order = new_order
        
        try:
            await session.commit()
            await session.refresh(new_order)
            logging.info("Заказ успешно создан!")
            return new_order
        except Exception as err:
            await session.rollback()
            logging.error("Ошибка, не удалось создать заказ!")