from sqlalchemy import select
from bot.database.models import Category
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class CategoryDAO(BaseDAO):
    model = Category
    
    @classmethod
    async def create_category(cls, name: str, session: AsyncSession) -> Category | None:
        new_category = cls.model(name=name)
        try:
            session.add(new_category)
            await session.commit()
            await session.refresh(new_category)
            logging.info("Категория создана!")
            return new_category
        except Exception as err:
            logging.error(f"Произошла ошибка при создании категории: {err}")
            await session.rollback()
            
    @classmethod
    async def get_all_categories(cls, session: AsyncSession) -> list[Category]:
        stmt = select(cls.model)
        result = await session.execute(stmt)
        return result.scalars().all()
        