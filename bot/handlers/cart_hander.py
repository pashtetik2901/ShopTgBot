from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.utils.keyboards import InlineKeyboards, ReplyKeyboard
from bot.utils.states import CartStates
from bot.database.repositories.cart_item_repository import CartItemDAO
from bot.database.db import with_session
from sqlalchemy.ext.asyncio import AsyncSession

cart_router = Router()

@cart_router.message(Command("cart"))
@cart_router.message(F.text == "🛒 Корзина")
@with_session
async def show_cart(message: Message, session: AsyncSession = None):
    """Показать корзину"""
    cart_items = await CartItemDAO.get_products_from_cart(message.from_user.id, session)
    
    if not cart_items:
        keyboard = InlineKeyboards.get_cart_empty_keyboard()
        await message.answer("🛒 Ваша корзина пуста", reply_markup=keyboard)
        return
    
    # Формируем сообщение с товарами
    total = 0
    cart_text = "🛒 Ваша корзина:\n\n"
    
    for item in cart_items:
        product = item['product']
        quantity = item['quantity']
        item_total = product.price * quantity
        total += item_total
        
        cart_text += f"📦 {product.name}\n"
        cart_text += f"   💰 {product.price} руб. x {quantity} = {item_total} руб.\n\n"
    
    cart_text += f"💵 Общая сумма: <b>{total} руб.</b>"
    
    keyboard = InlineKeyboards.get_cart_keyboard(cart_items)
    await message.answer(cart_text, reply_markup=keyboard, parse_mode="HTML")

async def update_cart_message(message: Message, session: AsyncSession = None):
    """Обновить сообщение с корзиной"""
    cart_items = await CartItemDAO.get_products_from_cart(message.from_user.id, session)
    
    if not cart_items:
        keyboard = InlineKeyboards.get_cart_empty_keyboard()
        await message.edit_text("🛒 Ваша корзина пуста", reply_markup=keyboard)
        return
    
    # Формируем сообщение с товарами
    total = 0
    cart_text = "🛒 Ваша корзина:\n\n"
    
    for item in cart_items:
        product = item['product']
        quantity = item['quantity']
        item_total = product.price * quantity
        total += item_total
        
        cart_text += f"📦 {product.name}\n"
        cart_text += f"   💰 {product.price} руб. x {quantity} = {item_total} руб.\n\n"
    
    cart_text += f"💵 Общая сумма: <b>{total} руб.</b>"
    
    keyboard = InlineKeyboards.get_cart_keyboard(cart_items)
    await message.edit_text(cart_text, reply_markup=keyboard, parse_mode="HTML")

@cart_router.callback_query(F.data.startswith("add_to_cart_"))
@with_session
async def add_to_cart_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession = None):
    """Добавить товар в корзину"""
    product_id = int(callback.data.split("_")[3])
    
    # Добавляем товар в корзину (по умолчанию 1 шт)
    success = await CartItemDAO.add_item_to_cart(callback.from_user.id, product_id, 1, session)
    
    if success:
        await callback.answer("✅ Товар добавлен в корзину!")
    else:
        await callback.answer("❌ Ошибка при добавлении товара")

@cart_router.callback_query(F.data.startswith("remove_from_cart_"))
@with_session
async def remove_from_cart_handler(callback: CallbackQuery, session: AsyncSession = None):
    """Удалить товар из корзины"""
    # Правильно извлекаем ID элемента корзины из callback_data
    item_id = int(callback.data.split("_")[-1])  # Берем последний элемент
    
    success = await CartItemDAO.remove_item_from_cart(item_id, session)
    
    if success:
        await callback.answer("✅ Товар удален из корзины")
        # Обновляем сообщение с корзиной
        await update_cart_message(callback.message, session)
    else:
        await callback.answer("❌ Ошибка при удалении товара")

@cart_router.callback_query(F.data == "clear_cart")
@with_session
async def ask_clear_cart(callback: CallbackQuery, state: FSMContext, session: AsyncSession = None):
    """Спросить подтверждение очистки корзины"""
    # Проверяем, есть ли товары в корзине
    cart_items = await CartItemDAO.get_products_from_cart(callback.from_user.id, session)
    
    if not cart_items:
        await callback.answer("🛒 Корзина уже пуста!")
        return
    
    keyboard = InlineKeyboards.get_confirm_clear_keyboard()
    await callback.message.edit_text(
        "❓ Вы уверены, что хотите очистить корзину?",
        reply_markup=keyboard
    )
    await state.set_state(CartStates.confirm_clear)

@cart_router.callback_query(F.data == "confirm_clear_cart", CartStates.confirm_clear)
@with_session
async def confirm_clear_cart(callback: CallbackQuery, state: FSMContext, session: AsyncSession = None):
    """Подтвердить очистку корзины"""
    success = await CartItemDAO.clear_cart(callback.from_user.id, session)
    
    if success:
        await callback.message.edit_text("🗑️ Корзина очищена")
    else:
        await callback.message.edit_text("❌ Ошибка при очистке корзины")
    
    await state.clear()

@cart_router.callback_query(F.data == "cancel_clear_cart", CartStates.confirm_clear)
@with_session
async def cancel_clear_cart(callback: CallbackQuery, state: FSMContext, session: AsyncSession = None):
    """Отменить очистку корзины"""
    await state.clear()
    # Перезагружаем корзину
    await update_cart_message(callback.message, session)

# @cart_router.callback_query(F.data == "create_order")
# @with_session
# async def create_order_handler(callback: CallbackQuery, session: AsyncSession = None):
#     """Оформить заказ"""
#     cart_items = await CartItemDAO.get_products_from_cart(callback.from_user.id, session)
    
#     if not cart_items:
#         await callback.answer("🛒 Корзина пуста!")
#         return
    
#     await callback.answer("Функция оформления заказа в разработке")

@cart_router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog_handler(callback: CallbackQuery):
    """Вернуться в каталог"""
    from bot.handlers.user_catalog_handler import show_categories
    await callback.message.delete()
    await show_categories(callback.message)