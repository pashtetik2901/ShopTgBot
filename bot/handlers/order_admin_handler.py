from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.database.repositories.order_repository import OrderDAO
from bot.utils.keyboards import ReplyKeyboard, InlineKeyboards
from bot.utils.states import AdminOrderStates
from bot.database.db import with_session
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.states import StatusState
import logging

admin_order_router = Router()

@admin_order_router.message(F.text == "📦 Управление заказами", StatusState.admin)
@with_session
async def manage_orders_handler(message: Message, session: AsyncSession = None):
    """Показать все заказы"""
    orders = await OrderDAO.get_all_order(session)
    
    if not orders:
        await message.answer("📦 Заказы отсутствуют")
        return
    
    keyboard = InlineKeyboards.get_orders_keyboard(orders)
    await message.answer("📦 Список заказов:", reply_markup=keyboard)

@admin_order_router.callback_query(F.data.startswith("order_"))
@with_session
async def show_order_detail(callback: CallbackQuery, session: AsyncSession = None):
    """Показать детали заказа"""
    order_id = int(callback.data.split("_")[1])
    order = await OrderDAO.get_ones_by_id(order_id, session)
    
    if not order:
        await callback.answer("Заказ не найден")
        return
    
    # Формируем информацию о заказе
    order_text = (
        f"📦 Заказ #{order.uid}\n\n"
        f"👤 Пользователь: {order.user.name if order.user else 'Неизвестно'}\n"
        f"💰 Сумма: {order.total_price} руб.\n"
        f"🚚 Доставка: {order.delivery_method}\n"
        f"🏠 Адрес: {order.user.address}\n"
        f"📊 Статус: {order.status}\n\n"
        f"📅 Создан: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    )
    
    # Добавляем товары
    if order.order_item:
        order_text += "\n🛍️ Товары:\n"
        for item in order.order_item:
            order_text += f"   • {item.product.name} x{item.quantity} - {item.product.price * item.quantity} руб.\n"
    
    keyboard = InlineKeyboards.get_order_actions_keyboard(order_id, order.status)
    await callback.message.edit_text(order_text, reply_markup=keyboard)
    await callback.answer()

@admin_order_router.callback_query(F.data.startswith("change_status_"))
async def ask_new_status(callback: CallbackQuery, state: FSMContext):
    """Запросить новый статус заказа"""
    order_id = int(callback.data.split("_")[2])
    
    await state.update_data(order_id=order_id)
    
    keyboard = InlineKeyboards.get_status_options_keyboard()
    await callback.message.edit_text(
        "📊 Выберите новый статус заказа:",
        reply_markup=keyboard
    )
    
    await state.set_state(AdminOrderStates.choose_status)
    await callback.answer()

@admin_order_router.callback_query(F.data.startswith("status_"), AdminOrderStates.choose_status)
@with_session
async def change_order_status(callback: CallbackQuery, state: FSMContext, session: AsyncSession = None):
    """Изменить статус заказа"""
    new_status = callback.data.split("_")[1]
    data = await state.get_data()
    order_id = data.get('order_id')
    
    success = await OrderDAO.update_status(order_id, new_status, session)
    
    if success:
        await callback.message.edit_text(f"✅ Статус заказа изменен на: {new_status}")
        
        # Отправляем уведомление пользователю (если нужно)
        order = await OrderDAO.get_ones_by_id(order_id, session)
        if order and order.user:
            try:
                await callback.bot.send_message(
                    chat_id=order.user.telegram_id,
                    text=f"📦 Статус вашего заказа #{order.uid} изменен на: {new_status}"
                )
            except Exception as e:
                logging.error(f"Не удалось отправить уведомление пользователю: {e}")
    else:
        await callback.message.edit_text("❌ Ошибка при изменении статуса")
    
    await state.clear()
    await callback.answer()