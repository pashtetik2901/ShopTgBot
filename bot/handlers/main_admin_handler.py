from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.repositories.user_repository import UserDAO
from bot.database.repositories.product_repository import ProductDAO
from bot.database.repositories.category_repository import CategoryDAO
from bot.database.models import User, Carts
from bot.database.db import with_session
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.messages import Messages
from bot.utils.keyboards import ReplyKeyboard, InlineKeyboards
from bot.utils.states import StatusState, AddProductState
from bot.utils.local_manager import LocalManager
from bot.config import Config

main_admin_router = Router()


@main_admin_router.message(Command("admin"))
async def hello_admin_handler(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    if telegram_id not in Config.ADMIN_IDS:
        await message.answer("Вы не администратор!")
        return

    await message.answer(
        "Добро пожаловать в панель администратора!",
        reply_markup=ReplyKeyboard.menu_admin_keyboard()
    )
    await state.set_state(StatusState.admin)


@main_admin_router.message(F.text == Messages.EXIT, StatusState.admin)
async def exit_admin_handler(message: Message, state: FSMContext):
    await message.answer("Вы вышли из панели администратора!")
    await state.clear()