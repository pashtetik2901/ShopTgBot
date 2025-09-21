from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload, joinedload
from typing import Any, List
from bot.database.models import Products, Order, User, OredrItem, Carts, CartItems
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from bot.database.repositories.cart_repository import CartDAO

class CartItemDAO(BaseDAO):
    model = CartItems
    model_cart = Carts
    model_user = User
    model_product = Products
    
    @classmethod
    async def get_cart_total(cls, user_id: int, session: AsyncSession) -> float:
        """Получить общую сумму корзины"""
        cart_items = await cls.get_products_from_cart(user_id, session)
        total = 0
        for item in cart_items:
            total += item['product'].price * item['quantity']
        return total
    
    @classmethod
    async def get_cart_with_items(cls, telegram_id: int, session: AsyncSession) -> Carts:
        """Получить корзину с товарами"""
        stmt = select(cls.model_cart).options(
            selectinload(cls.model_cart.cart_item).joinedload(CartItems.product)
        ).join(cls.model_user).where(cls.model_user.telegram_id == telegram_id)
        
        result = await session.execute(stmt)
        cart = result.scalars().first()
        return cart
    
    @classmethod
    async def get_products_from_cart(cls, user_id: int, session: AsyncSession):
        try:
            # Находим корзину пользователя
            stmt = select(Carts).where(Carts.user_id == user_id)
            result = await session.execute(stmt)
            cart = result.scalars().first()
            
            if not cart:
                logging.warning(f"Корзина не найдена для пользователя {user_id}")
                return []
            
            # Получаем все элементы корзины с информацией о товарах
            stmt = select(cls.model).options(
                selectinload(cls.model.product)
            ).where(cls.model.cart_id == cart.id)
            
            result = await session.execute(stmt)
            cart_items = result.scalars().all()
            
            # Форматируем результат
            items_with_info = []
            for item in cart_items:
                items_with_info.append({
                    'id': item.id,
                    'product': item.product,
                    'quantity': item.quantity
                })
            
            return items_with_info
            
        except Exception as err:
            logging.error(f"Ошибка при получении товаров из корзины: {err}")
            return []
        
    @classmethod
    async def add_item_to_cart(cls, user_id: int, product_id: int, quantity: int, session: AsyncSession):
        try:
            # Получаем или создаем корзину
            cart = await CartDAO.get_or_create_cart(user_id, session)
            if not cart:
                logging.error("Не удалось получить или создать корзину")
                return False
            
            # Проверяем, есть ли уже такой товар в корзине
            stmt = select(cls.model).where(
                (cls.model.cart_id == cart.id) & 
                (cls.model.product_id == product_id)
            )
            result = await session.execute(stmt)
            existing_item = result.scalars().first()
            
            if existing_item:
                # Обновляем количество
                existing_item.quantity += quantity
            else:
                # Добавляем новый товар
                new_item = cls.model(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity
                )
                session.add(new_item)
            
            await session.commit()
            logging.info(f"Товар {product_id} добавлен в корзину пользователя {user_id}")
            return True
            
        except Exception as err:
            logging.error(f"Ошибка при добавлении товара в корзину: {err}")
            await session.rollback()
            return False
        
    @classmethod
    async def remove_item_from_cart(cls, item_id: int, session: AsyncSession):
        try:
            # Сначала находим элемент корзины
            stmt = select(cls.model).where(cls.model.id == item_id)
            result = await session.execute(stmt)
            cart_item = result.scalars().first()
            
            if not cart_item:
                logging.error("Элемент корзины не найден")
                return False
            
            # Удаляем элемент
            await session.delete(cart_item)
            await session.commit()
            logging.info("Товар удален из корзины")
            return True
            
        except Exception as err:
            logging.error(f"Ошибка при удалении товара из корзины: {err}")
            await session.rollback()
            return False
    
    @classmethod
    async def clear_cart(cls, telegram_id: int, session: AsyncSession):
        """Очистить корзину"""
        cart = await cls.get_cart_with_items(telegram_id, session)
        
        if cart:
            stmt = delete(cls.model).where(cls.model.cart_id == cart.id)
            await session.execute(stmt)
            
            try:
                await session.commit()
                return True
            except Exception as err:
                await session.rollback()
                logging.error(f"Ошибка при очистке корзины: {err}")
                return False
        return False