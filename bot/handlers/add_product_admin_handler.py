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

add_prd_admin_router = Router()

manager = LocalManager()

@add_prd_admin_router.message(Command("admin"))
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


@add_prd_admin_router.message(F.text == Messages.EXIT, StatusState.admin)
async def exit_admin_handler(message: Message, state: FSMContext):
    await message.answer("Вы вышли из панели администратора!")
    await state.clear()


@add_prd_admin_router.message(F.text == Messages.ADD_PRODUCT_ADMIN, StatusState.admin)
@with_session
async def add_product_admin_handler(message: Message, state: FSMContext, session: AsyncSession):
    category_list = await CategoryDAO.get_all_categories(session)
    if len(category_list) <= 0:
        await message.answer("Нет категорий, создайте новую!")
    else:
        await message.answer(
            text="Выберите категорию, если ее не существует введите название",
            reply_markup=ReplyKeyboard.catalog_keyboard(category_list)
        )
    await state.set_state(AddProductState.wait_category)
    
@add_prd_admin_router.message(AddProductState.wait_category)
@with_session
async def add_category_handler(message: Message, state: FSMContext, session: AsyncSession):
    name_category = message.text
    category = await CategoryDAO.create_category(name_category, session)
    if category is None:
        await message.answer(text='Произошла ошибка при создании категории')
        await state.clear()
        return
    await state.update_data(category_name=category.name)
    await message.answer("Введите название товара")
    await state.set_state(AddProductState.wait_name)
    
@add_prd_admin_router.message(AddProductState.wait_name)
async def add_name_product_handler(message: Message, state: FSMContext):
    name_product = message.text
    await state.update_data(name_product=name_product)
    await message.answer("Введите описание товара")
    await state.set_state(AddProductState.wait_description)
    
@add_prd_admin_router.message(AddProductState.wait_description)
async def add_description_product_handler(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.answer("Введите стоимость товара")
    await state.set_state(AddProductState.wait_price)
    
@add_prd_admin_router.message(AddProductState.wait_price)
async def add_price_product_handler(message: Message, state: FSMContext):
    price = message.text
    await state.update_data(price=price)
    await message.answer("Пришлите фото товара")
    await state.set_state(AddProductState.wait_photo)
    
@add_prd_admin_router.message(AddProductState.wait_photo)
@with_session
async def add_photo_product_handler(message: Message, state: FSMContext, session: AsyncSession):
    photo = message.photo[-1]
    file_id = photo.file_id
    
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    file_bytes = await message.bot.download_file(file_path)
    filename = f'{file_id}.png'
    save_path = manager.save_photo(file_bytes.read(), filename)
    
    data = await state.get_data()
    
    product = await ProductDAO.create_product(
        category_name=data.get("category_name"),
        name=data.get("name_product"),
        description=data.get("description"),
        price=data.get("price"),
        photo_url=save_path,
        session=session
    )
    if product is None:
        await message.answer("Произошла ошибка с добавлением товара", reply_markup=ReplyKeyboard.menu_admin_keyboard())
        await state.set_state(StatusState.admin)
        return
    await message.answer("Продукт успешно добавлен", reply_markup=ReplyKeyboard.menu_admin_keyboard())
    await state.set_data()
    await state.set_state(StatusState.admin)
    
    
    