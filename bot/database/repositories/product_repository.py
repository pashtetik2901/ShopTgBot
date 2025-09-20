from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import Any
from bot.database.models import Products, Category
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging


class ProductDAO(BaseDAO):
    model = Products
    model_category = Category
    
    
    @classmethod
    async def refresh_product(cls, product_id:int, data: dict[str, Any], session: AsyncSession):
        stmt = select(cls.model).where(cls.model.id == product_id)
        result = await session.execute(stmt)
        product = result.scalars().first()
        if product is None:
            logging.error("Ошибка, товар не найден!")
            return
        keys_list = list(data.keys())
        
        if "name" in keys_list:
            product.name = data.get("name")
        if "description" in keys_list:
            product.description = data.get("description")
        if "price" in keys_list:
            product.price = data.get("price")
        if "photo_url" in keys_list:
            product.photo_url = data.get("photo_url")
        
        try:
            await session.commit()
            await session.refresh(product)
            logging.info("Редактирование успешно!")
            return product
        except Exception as err:
            await session.rollback()
            logging.error(f"Ошибка, редактирование не удалось: {err}")
    
    @classmethod
    async def get_products_from_category(cls, category_id: int, session: AsyncSession):
        stmt = select(cls.model).where(cls.model.category_id == category_id)
        result = await session.execute(stmt)
        product_list = result.scalars().all()
        return product_list
    
    @classmethod
    async def delete_product(cls, product_id: int, session: AsyncSession):
        stmt = delete(cls.model).where(cls.model.id == product_id)
        try:
            await session.execute(stmt)
            await session.commit()
            logging.info("Товар успешно удален!")
        except Exception as err:
            logging.error(f"Ошибка, не удалось удалить товар: {err}")
            await session.rollback()


    @classmethod
    async def create_product(cls, category_name: str, name: str, description: str, 
                price: float, photo_url: str, session: AsyncSession) -> Products | None:
        new_product = cls.model(
            name=name,
            description=description,
            price=price,
            photo_url=photo_url
        )      
        
        stmt = select(cls.model_category).options(
                selectinload(cls.model_category.product)
            ).where(cls.model_category.name == category_name)
        result = await session.execute(stmt)
        category = result.scalars().first()
        
        if category:
            try:
                category.product.append(new_product)
                await session.commit()
                await session.refresh(new_product)
                logging.info("Товар успешно создан!")
                return new_product
            except Exception as err:
                logging.error(f"Ошибка при создании товара!\n{err}")
                await session.rollback()
        else:
            logging.error(f"Ошибка, категория({category_name}) не найдена!")