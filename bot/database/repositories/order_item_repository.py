from sqlalchemy import select, delete
from typing import Any
from bot.database.models import Products, Order, User, OredrItem, Carts
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class OrderItemDAO(BaseDAO):
    model = OredrItem
    model_cart = Carts
    model_order = Order
        
    @classmethod
    async def create_order_item(cls, order_id: int, session: AsyncSession):
        stmt = select(cls.model_order).where(cls.model_order.id == order_id)
        result = await session.execute(stmt)
        order = result.scalars().first()
        if order is None:
            logging.error("Ошибка, заказ не найден!")
            return
        user_id = order.user_id
        stmt = select(cls.model_cart).where(cls.model_cart.user_id == user_id)
        result = await session.execute(stmt)
        cart = result.scalars().first()
        if cart is None:
            logging.error("Ошибка, корзина не найдена!")
            return
        product_list = cart.cart_item
        
        for cart_item in product_list:
            product = cart_item.product
            quintety = cart_item.quantity
            new_order_item = cls.model(
                product=product,
                quantity=quintety
            )
            order.order_item.append(new_order_item)
            
        try:
            await session.commit()
            await session.refresh(new_order_item)
            logging.info("Товар добавлен в заказ")
            return new_order_item
        except Exception as err:
            await session.rollback()
            logging.error(f"Ошибка при создании OrderItem - {err}")
        
            
        
        
            
    