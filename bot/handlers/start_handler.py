from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.database.repositories.user_repository import UserDAO
from bot.database.repositories.cart_repository import CartDAO
from bot.database.models import User, Carts
from bot.database.db import with_session
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.keyboards import ReplyKeyboard

start_router = Router()

@start_router.message(Command("start"))
@with_session
async def hello_handler(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    telegram_id = message.from_user.id
    
    user = await UserDAO.add_first_user(telegram_id, session)
    if user is None:
        await message.answer("Ошибка, обратитесь к администратору!")
        return
    if user == True:
        await message.answer("Здравствуйте, это бот интернет-магазин!!!", reply_markup=ReplyKeyboard.get_main_menu_keyboard())
        return
    cart = await CartDAO.create_cart(user.id, session)
    if cart is None:
        await message.answer("Ошибка, обратитесь к администратору!")
        return
    await message.answer("Здравствуйте, это бот интернет-магазин!!!", reply_markup=ReplyKeyboard.get_main_menu_keyboard())
    

        
    
    
    