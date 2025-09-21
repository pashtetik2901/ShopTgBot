from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from bot.database.repositories.user_repository import UserDAO
from bot.database.repositories.cart_repository import CartDAO
from bot.database.repositories.category_repository import CategoryDAO
from bot.database.repositories.product_repository import ProductDAO, Products
from bot.database.repositories.cart_item_repository import CartItemDAO
from bot.utils.keyboards import InlineKeyboards, ReplyKeyboard
from bot.database.models import User, Carts
from bot.database.db import with_session
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.states import CartStates
import os

user_catalog_router = Router()

@user_catalog_router.message(Command("catalog"))
@user_catalog_router.message(F.text == "🛍️ Каталог")
@with_session
async def show_categories(message: Message, session: AsyncSession):
    categories = await CategoryDAO.get_all_notes(session)
    
    if not categories:
        await message.answer("Категории товаров пока отсутствуют.")
        return
    
    keyboard = InlineKeyboards.get_categories_keyboard(categories)
    await message.answer("🏪 Выберите категорию товаров:", reply_markup=keyboard)

@user_catalog_router.callback_query(F.data.startswith("category_"))
@with_session
async def show_category_products(callback: CallbackQuery, session: AsyncSession = None):
    category_id = int(callback.data.split("_")[1])
    category = await CategoryDAO.get_ones_by_id(category_id, session)
    
    if not category:
        await callback.answer("Категория не найдена")
        return
    
    products = await ProductDAO.get_products_from_category(category_id, session)
    
    if not products:
        keyboard = InlineKeyboards.get_empty_category_keyboard()
        await callback.message.edit_text(
            f"В категории '{category.name}' пока нет товаров.",
            reply_markup=keyboard
        )
        return
    
    keyboard = InlineKeyboards.get_products_keyboard(products, category_id)
    await callback.message.edit_text(
        f"📦 Товары в категории '{category.name}':",
        reply_markup=keyboard
    )
    await callback.answer()

@user_catalog_router.callback_query(F.data.startswith("product_"))
@with_session
async def show_product_detail(callback: CallbackQuery, session: AsyncSession = None):
    product_id = int(callback.data.split("_")[1])
    product: Products = await ProductDAO.get_ones_by_id(product_id, session)
    
    if not product:
        await callback.answer("Товар не найден")
        return
    
    # Формируем описание товара
    description = f"🏷️ <b>{product.name}</b>\n\n"
    description += f"📝 {product.description}\n\n"
    description += f"💰 Цена: <b>{product.price} руб.</b>\n"
    
    # Получаем ID категории для кнопки возврата
    category_id = product.category_id if hasattr(product, 'category_id') else None
    
    keyboard = InlineKeyboards.get_product_detail_keyboard(product_id, category_id)
    
    # Если есть фото товара
    if product.photo_url:
        await callback.message.delete()  # Удаляем предыдущее сообщение
        
        # Проверяем, является ли photo_url локальным путем
        if product.photo_url.startswith(('http://', 'https://')):
            # Это веб-URL - отправляем напрямую
            await callback.message.answer_photo(
                photo=product.photo_url,
                caption=description,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            # Это локальный путь - отправляем как файл
            try:
                # Убедитесь, что путь корректен и файл существует
                if os.path.exists(product.photo_url):
                    photo = FSInputFile(product.photo_url)
                    await callback.message.answer_photo(
                        photo=photo,
                        caption=description,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                else:
                    # Если файл не найден, отправляем только текст
                    await callback.message.answer(
                        description,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
            except Exception as e:
                # В случае ошибки отправляем только текст
                print(f"Ошибка при отправке фото: {e}")
                await callback.message.answer(
                    description,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
    else:
        await callback.message.edit_text(
            description,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    await callback.answer()

# Остальной код остается без изменений...
@user_catalog_router.callback_query(F.data.startswith("add_to_cart_"))
async def ask_quantity_handler(callback: CallbackQuery, state: FSMContext):
    """Спросить количество товара"""
    product_id = int(callback.data.split("_")[3])
    
    await state.update_data(product_id=product_id)
    await state.set_state(CartStates.waiting_quantity)
    
    keyboard = InlineKeyboards.get_quantity_keyboard(product_id)
    
    await callback.message.answer(
        "📦 Выберите количество товара:",
        reply_markup=keyboard
    )
    await callback.answer()

@user_catalog_router.callback_query(F.data.startswith("quantity_"), CartStates.waiting_quantity)
@with_session
async def process_quantity_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession = None):
    """Обработать выбор количества"""
    data = callback.data.split("_")
    product_id = int(data[1])
    quantity = int(data[2])
    
    # Добавляем товар в корзину с выбранным количеством
    success = await CartItemDAO.add_item_to_cart(callback.from_user.id, product_id, quantity, session)
    
    if success:
        await callback.message.answer(f"✅ Добавлено {quantity} шт. в корзину!")
    else:
        await callback.message.answer("❌ Ошибка при добавлении товара")
    
    await state.clear()
    await callback.message.delete()  # Удаляем сообщение с выбором количества

@user_catalog_router.callback_query(F.data == "cancel_quantity", CartStates.waiting_quantity)
async def cancel_quantity_handler(callback: CallbackQuery, state: FSMContext):
    """Отменить выбор количества"""
    await state.clear()
    await callback.message.delete()
    await callback.answer("❌ Добавление отменено")

@user_catalog_router.callback_query(F.data == "back_to_categories")
@with_session
async def back_to_categories(callback: CallbackQuery, session: AsyncSession = None):
    categories = await CategoryDAO.get_all_notes(session)
    
    if not categories:
        await callback.answer("Категории отсутствуют")
        return
    
    keyboard = InlineKeyboards.get_categories_keyboard(categories)
    await callback.message.edit_text(
        "🏪 Выберите категорию товаров:",
        reply_markup=keyboard
    )
    await callback.answer()