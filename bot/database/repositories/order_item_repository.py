from sqlalchemy import select, delete, join
from sqlalchemy.orm import selectinload, joinedload
from typing import Any
from bot.database.models import Products, Order, User, OredrItem, Carts, CartItems
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class OrderItemDAO(BaseDAO):
    model = OredrItem
    model_cart = Carts
    model_order = Order
        
    @classmethod
    async def create_order_item(cls, order_id: int, session: AsyncSession):
        try:
            # Получаем заказ с пользователем
            stmt = select(Order).options(
                selectinload(Order.user)
            ).where(Order.id == order_id)
            
            result = await session.execute(stmt)
            order = result.scalars().first()
            
            if order is None:
                logging.error("Ошибка, заказ не найден!")
                return None
            
            user_id = order.user_id
            logging.info(f"Создание order items для заказа {order_id}, пользователь {user_id}")
            
            # Получаем корзину пользователя с товарами
            stmt = select(Carts).options(
                selectinload(Carts.cart_item).joinedload(CartItems.product)
            ).where(Carts.user_id == user_id)
            
            result = await session.execute(stmt)
            cart = result.scalars().first()
            
            if cart is None or not cart.cart_item:
                logging.error("Ошибка, корзина не найдена или пуста!")
                return None
            
            # Создаем OrderItem для каждого товара в корзине
            order_items_created = 0
            for cart_item in cart.cart_item:
                try:
                    if not cart_item.product:
                        logging.warning(f"Пропускаем cart_item {cart_item.id} - товар не найден")
                        continue
                    
                    # Создаем новый OrderItem
                    new_order_item = OredrItem(
                        order_id=order_id,
                        product_id=cart_item.product_id,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price * cart_item.quantity  # Общая цена за количество
                    )
                    
                    session.add(new_order_item)
                    order_items_created += 1
                    logging.info(f"Добавлен товар {cart_item.product.name} x{cart_item.quantity}")
                    
                except Exception as item_error:
                    logging.error(f"Ошибка при создании order item для товара {cart_item.product_id}: {item_error}")
                    continue
            
            if order_items_created > 0:
                # Очищаем корзину после успешного создания заказа
                try:
                    delete_stmt = delete(CartItems).where(CartItems.cart_id == cart.id)
                    await session.execute(delete_stmt)
                    logging.info(f"Корзина пользователя {user_id} очищена")
                except Exception as clear_error:
                    logging.error(f"Ошибка очистки корзины: {clear_error}")
                
                await session.commit()
                logging.info(f"Успешно создано {order_items_created} товаров для заказа {order_id}")
                return True
            else:
                logging.warning("Нет товаров для добавления в заказ")
                await session.rollback()
                return False
                
        except Exception as err:
            await session.rollback()
            logging.error(f"Ошибка при создании OrderItem - {err}")
            return False
        
            
        
        
            
    