from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

class BaseDAO:
    model = None

    @classmethod
    async def get_ones_by_id(cls, id: int, session: AsyncSession):
        stmt = select(cls.model).where(cls.model.id == id)
        result = await session.execute(stmt)
        ones = result.scalars().first()
        return ones
        
    @classmethod
    async def delete_ones_by_id(cls, id: int, session: AsyncSession):
        stmt = delete(cls.model).where(cls.model.id == id)
        try:
            await session.execute(stmt)
            await session.commit()
        except SQLAlchemyError as err:
            await session.rollback()
            raise err