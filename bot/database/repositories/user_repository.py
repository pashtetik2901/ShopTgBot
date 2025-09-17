from sqlalchemy import select
from bot.database.models import User
from bot.database.repositories.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO(BaseDAO):
    model = User

    async def get_by_telegram_id(self, telegram_id: int,  session: AsyncSession):
        stmt = select(self.model).filter_by(telegram_id=telegram_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, username: str, session: AsyncSession):
        stmt = select(self.model).filter(self.model.username.ilike(username))
        result = await session.execute(stmt)
        return result.scalars().first()