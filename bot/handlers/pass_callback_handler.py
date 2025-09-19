from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.repositories.user_repository import UserDAO
from bot.database.repositories.cart_repository import CartDAO
from bot.database.models import User, Carts
from bot.database.db import with_session
from sqlalchemy.ext.asyncio import AsyncSession

pass_callback_router = Router()

@pass_callback_router.callback_query(F.data.startswith("pass"))
async def pass_handler(callback: CallbackQuery):
    await callback.answer("Pass")
