from sqlalchemy import select, delete
from typing import Any
from bot.database.models import Products, Order, User, OredrItem, Carts, CartItems
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class CartItemDAO(BaseDAO):
    model = CartItems
    model_cart = Carts
    model_user = User
    model_product = Products
    
    
    @classmethod
    async def create_item(cls, telegram_id: int, product_id: int, quantity: int, session: AsyncSession):
        stmt = select(cls.model_user).where(cls.model_user.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user is None:
            logging.error("Ошибка, пользователь не найден")
            return
        cart = user.carts
        if cart is None:
            logging.error("Ошибка, нет корзины")
            return
        stmt = select(cls.model_product).where(cls.model_product.id == product_id)
        result = await session.execute(stmt)
        product = result.scalars().first()
        if product is None:
            logging.error("Ошибка, товар не найден!")
            return
        new_cart_item = cls.model(
            product=product,
            quantity=quantity
        )
        cart.cart_item.append(new_cart_item)
        try:
            await session.commit()
            await session.refresh(cart)
            logging.info()
            return cart
        except Exception as err:
            await session.rollback()
            logging.error("Ошибка с добавлением товара!")