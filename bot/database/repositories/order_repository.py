from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import Any
from bot.database.models import Products, Order, User
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class OrderDAO(BaseDAO):
    model = Order
    model_user = User
    
    @classmethod
    async def get_ones_by_id(cls, id: int, session: AsyncSession):
        stmt = select(cls.model).options(
            selectinload(cls.model.user)    
        ).where(cls.model.id == id)
        result = await session.execute(stmt)
        ones = result.scalars().first()
        return ones
    
    @classmethod
    async def update_status(cls, order_id: int, new_status: str, session: AsyncSession):
        stmt = select(cls.model).where(cls.model.id == order_id)
        result = await session.execute(stmt)
        order = result.scalars().first()
        
        if order is None:
            logging.error("Ошибка, заказ не найден")
            return False
        
        order.status = new_status
        
        try:
            await session.commit()
            await session.refresh(order)
            logging.info("Статус успешно изменен")
            return True
        except Exception as err:
            await session.rollback()
            logging.error(f"Ошибка изменения статуса: {err}")
            return False
    
    @classmethod
    async def get_all_order(cls, session: AsyncSession) -> list[Order]:
        stmt = select(cls.model)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def create_order(cls, telegram_id: int, uid: str, delivery_method: str, status: str, total_price: float, session: AsyncSession):
        try:
            # Находим пользователя
            # logging.warning("Ищем пользователя")
            
            stmt = select(cls.model_user).options(
                selectinload(cls.model_user.order)
            ).where(cls.model_user.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            
            if user is None:
                logging.info("Пользователь не найден!")
                return None
            
            if user.order is not None:
                logging.warning("У пользователя уже есть заказ")
                return False
            
            # logging.warning(f"Пользователь найден его айди {user.id}")
            
            # Создаем новый заказ с правильной связью
            new_order = cls.model(
                uid=uid,
                delivery_method=delivery_method,
                status=status,
                total_price=total_price,
                user=user  # Добавляем user_id для связи
            )
            
            # logging.warning("Заказ создан но не сохранен")
            
            # Добавляем заказ в сессию
            session.add(new_order)
            # await session.flush()  # Используем flush вместо commit для получения ID
            await session.commit()
            await session.refresh(new_order)
            
            logging.info("Заказ успешно создан!")
            return new_order
            
        except Exception as err:
            logging.error(f"Ошибка, не удалось создать заказ!: {err}")
            await session.rollback()
            return None