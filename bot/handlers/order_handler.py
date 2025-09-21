from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.database.repositories.order_repository import OrderDAO
from bot.database.repositories.user_repository import UserDAO
from bot.database.repositories.order_item_repository import OrderItemDAO
from bot.database.repositories.cart_repository import CartDAO
from bot.database.repositories.cart_item_repository import CartItemDAO
from bot.utils.keyboards import ReplyKeyboard, InlineKeyboards
from bot.utils.states import OrderStates
from bot.database.db import with_session
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging
import re

order_router = Router()

# Начало оформления заказа
@order_router.callback_query(F.data == "create_order")
@with_session
async def start_order_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession = None):
    """Начало оформления заказа - проверка корзины"""
    user_id = callback.from_user.id
    logging.info(f"Начало оформления заказа для пользователя ID: {user_id}")
    
    # Проверяем, есть ли товары в корзине
    cart_items = await CartItemDAO.get_products_from_cart(user_id, session)
    if not cart_items:
        await callback.answer("🛒 Корзина пуста!", show_alert=True)
        return
    
    # Получаем общую сумму
    total_price = await CartItemDAO.get_cart_total(user_id, session)
    
    # Сохраняем данные в состоянии
    await state.update_data(
        total_price=total_price,
        user_id=user_id
    )
    
    # Запрашиваем имя
    await callback.message.answer(
        "📝 Для оформления заказа нам нужны ваши данные\n\n"
        "👤 Введите ваше имя:"
    )
    
    await state.set_state(OrderStates.enter_name)
    await callback.answer()

# Ввод имени
@order_router.message(OrderStates.enter_name)
async def enter_name_handler(message: Message, state: FSMContext):
    """Обработчик ввода имени"""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Введите ваше настоящее имя:")
        return
    
    await state.update_data(customer_name=name)
    
    # Запрашиваем телефон
    await message.answer(
        f"👤 Имя: {name}\n\n"
        "📞 Теперь введите ваш номер телефона:\n"
        "Формат: +7 XXX XXX XX XX или 8 XXX XXX XX XX"
    )
    
    await state.set_state(OrderStates.enter_phone)

# Ввод телефона
@order_router.message(OrderStates.enter_phone)
async def enter_phone_handler(message: Message, state: FSMContext):
    """Обработчик ввода телефона"""
    phone = message.text.strip()
    
    # Проверяем формат телефона
    phone_pattern = r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
    if not re.match(phone_pattern, phone):
        await message.answer(
            "❌ Неверный формат номера телефона.\n"
            "Пожалуйста, введите номер в формате:\n"
            "+7 XXX XXX XX XX или 8 XXX XXX XX XX"
        )
        return
    
    await state.update_data(customer_phone=phone)
    
    # Получаем данные из состояния
    data = await state.get_data()
    total_price = data.get('total_price', 0)
    
    # Предлагаем выбрать способ доставки
    keyboard = InlineKeyboards.get_delivery_method_keyboard()
    await message.answer(
        f"👤 Имя: {data.get('customer_name')}\n"
        f"📞 Телефон: {phone}\n"
        f"💰 Сумма заказа: {total_price} руб.\n\n"
        "🚚 Выберите способ доставки:",
        reply_markup=keyboard
    )
    
    await state.set_state(OrderStates.choose_delivery)

# Выбор способа доставки
@order_router.callback_query(F.data.startswith("delivery_"), OrderStates.choose_delivery)
async def choose_delivery_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора способа доставки"""
    delivery_method = callback.data.split("_")[1]
    
    await state.update_data(delivery_method=delivery_method)
    
    if delivery_method == "pickup":
        # Для самовывоза сразу переходим к подтверждению
        await state.update_data(delivery_address="Самовывоз")
        await show_order_confirmation(callback.message, state)
    else:
        # Для доставки запрашиваем адрес
        await callback.message.answer(
            "🏠 Введите адрес доставки:\n"
            "Укажите город, улицу, дом и квартиру"
        )
        await state.set_state(OrderStates.enter_address)
    
    await callback.answer()

# Ввод адреса доставки
@order_router.message(OrderStates.enter_address)
async def enter_address_handler(message: Message, state: FSMContext):
    """Обработчик ввода адреса доставки"""
    address = message.text.strip()
    
    if len(address) < 10:
        await message.answer("❌ Адрес слишком короткий. Пожалуйста, укажите полный адрес:")
        return
    
    await state.update_data(delivery_address=address)
    await show_order_confirmation(message, state)

# Показать подтверждение заказа
async def show_order_confirmation(message: Message, state: FSMContext):
    """Показать информацию о заказе для подтверждения"""
    data = await state.get_data()
    
    order_summary = (
        f"📋 ПОДТВЕРЖДЕНИЕ ЗАКАЗА\n\n"
        f"👤 Имя: {data.get('customer_name')}\n"
        f"📞 Телефон: {data.get('customer_phone')}\n"
        f"🚚 Доставка: {data.get('delivery_method')}\n"
    )
    
    if data.get('delivery_method') != 'pickup':
        order_summary += f"🏠 Адрес: {data.get('delivery_address')}\n"
    
    order_summary += (
        f"💰 Сумма: {data.get('total_price')} руб.\n\n"
        f"✅ Все верно? Подтверждаем заказ?"
    )
    
    keyboard = InlineKeyboards.get_confirmation_keyboard()
    await message.answer(order_summary, reply_markup=keyboard)
    await state.set_state(OrderStates.confirm_order)

# Подтверждение заказа
@order_router.callback_query(F.data.startswith("confirm_"), OrderStates.confirm_order)
@with_session
async def confirm_order_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Обработчик подтверждения заказа"""
    action = callback.data.split("_")[1]
    
    if action == "yes":
        # Создаем заказ
        await create_final_order(callback, state, session)
    else:
        # Отмена заказа
        await callback.message.answer(
            "❌ Заказ отменен.\n"
            "Вы можете оформить заказ позже.",
            reply_markup=ReplyKeyboard.get_main_menu_keyboard()
        )
        await state.clear()
        await callback.answer("Заказ отменен")
    
    await callback.answer()

# Финальное создание заказа
async def create_final_order(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Финальное создание заказа"""
    try:
        data = await state.get_data()
        user_id = data.get('user_id')
        total_price = data.get('total_price')
        
        if not all([user_id, total_price]):
            await callback.message.answer("❌ Ошибка: данные заказа не найдены")
            return
        
        # Генерируем уникальный номер заказа
        order_uid = str(uuid.uuid4())[:8].upper()
        
        # Формируем информацию о доставке
        delivery_info = (
            f"{data.get('delivery_method')} - {data.get('delivery_address', 'Самовывоз')}"
        )
        
        await UserDAO.update_user(
            telegram_id=user_id,
            name=data.get('customer_name'),
            phone=data.get('customer_phone'),
            address=delivery_info,
            session=session
        )
        
        await callback.message.answer("Данные пользовател обновлены")
        
        await callback.message.answer(f"Айди пользователя {user_id}")
        
        # Создаем заказ
        order = await OrderDAO.create_order(
            telegram_id=user_id,
            uid=order_uid,
            # customer_name=data.get('customer_name'),
            # customer_phone=data.get('customer_phone'),
            delivery_method=delivery_info,
            status="pending",
            total_price=total_price,
            session=session
        )
        
        if order is None:
            await callback.message.answer("❌ Ошибка при создании заказа")
            return
        
        if order == False:
            await callback.message.answer("У вас уже есть активный заказ!")
            return
        
        await callback.message.answer("Заказ создан")
        
        # Добавляем товары в заказ
        success = await OrderItemDAO.create_order_item(order.id, session)
        if not success:
            await session.rollback()
            await callback.message.answer("❌ Ошибка при добавлении товаров в заказ")
            return
        
        await callback.message.answer("Товары добавлены в заказ")
        
        # Очищаем корзину
        await CartDAO.clear_user_cart(user_id, session)
        
        
        
        # Отправляем подтверждение
        order_details = (
            f"✅ ЗАКАЗ №{order_uid} ОФОРМЛЕН!\n\n"
            f"👤 Имя: {data.get('customer_name')}\n"
            f"📞 Телефон: {data.get('customer_phone')}\n"
            f"🚚 Доставка: {delivery_info}\n"
            f"💰 Сумма: {total_price} руб.\n\n"
            f"📦 Статус: В обработке\n\n"
            "Мы свяжемся с вами в ближайшее время для подтверждения заказа."
        )
        
        await callback.message.answer(
            order_details,
            reply_markup=ReplyKeyboard.get_main_menu_keyboard()
        )
        
        await state.clear()
        
    except Exception as e:
        await callback.message.answer(
            "❌ Произошла ошибка при оформлении заказа. Попробуйте позже.",
            reply_markup=ReplyKeyboard.get_main_menu_keyboard()
        )
        await state.clear()