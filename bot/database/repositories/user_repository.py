from sqlalchemy import select
from bot.database.models import User
from bot.database.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    async def get_by_telegram_id(self, telegram_id: int):
        stmt = select(self.model).filter_by(telegram_id=telegram_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, username: str):
        stmt = select(self.model).filter(self.model.username.ilike(username))
        result = await self.session.execute(stmt)
        return result.scalars().first()