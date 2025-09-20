from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.repositories.product_repository import ProductDAO
from bot.database.db import with_session
from bot.utils.keyboards import InlineKeyboards
from bot.utils.states import StatusState, RedactroState
from bot.utils.messages import Messages

redactor_prd_admin = Router()


@redactor_prd_admin.message(F.text == Messages.REDACTOR_PRODUCT_ADMIN, StatusState.admin)
@with_session
async def get_all_product_handler(message: Message, state: FSMContext, session: AsyncSession):
    product_list = await ProductDAO.get_all_notes(session)
    if len(product_list) <= 0:
        await message.answer("Нет товаров для редактирования")
    else:
        await message.answer(
            "Выберите товар, который нужно редактировать",
            reply_markup=InlineKeyboards.all_product(product_list)
        )
        
@redactor_prd_admin.callback_query(F.data.startswith("product_"))
async def select_product_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    # Ожидаем, что callback_data формата "product_<product_id>"
    _, product_id_str = query.data.split("_", 1)
    product_id = int(product_id_str)

    # Сохраняем product_id в состоянии и чистим предыдущие изменения
    await state.update_data(product_id=product_id, changed_data={})
    await state.set_state(RedactroState.choosing_field)

    # Отправляем меню редактирования выбранного товара
    await query.message.edit_text(
        "Выберите параметр для редактирования товара:",
        reply_markup=InlineKeyboards.build_edit_keyboard(product_id)
    )
    

@redactor_prd_admin.callback_query(F.data.startswith("rdc_"))
@with_session
async def choice_field_handler(query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await query.answer()
    _, action, product_id_str = query.data.split("_", 2)
    product_id = int(product_id_str)

    if action == "save":
        state_data = await state.get_data()
        changed_data = state_data.get("changed_data", {})

        if not changed_data:
            await query.message.answer("Нет изменений для сохранения.")
            return

        # Используем переданный session напрямую
        result = await ProductDAO.refresh_product(product_id, changed_data, session)
        if result:
            await query.message.edit_text(
                f"Товар успешно обновлен:\n\n"
                f"Название: {result.name}\n"
                f"Описание: {result.description}\n"
                f"Цена: {result.price}\n"
                f"Фото URL: {result.photo_url}"
            )
            await state.clear()
        else:
            await query.message.answer("Ошибка при сохранении товара.")
        return

    if action == "cancel":
        await query.message.edit_text("Редактирование отменено.")
        await state.clear()
        return

    field = action  # name, description, price, photo_url
    await state.update_data(field=field, product_id=product_id)

    prompt = {
        "name": "Введите новое название товара",
        "description": "Введите новое описание товара",
        "price": "Введите новую цену товара",
        "photo_url": "Введите новый URL фото товара"
    }.get(field, "Введите новое значение")

    await query.message.answer(prompt)
    await state.set_state(RedactroState.waiting_for_value)


@redactor_prd_admin.message(RedactroState.waiting_for_value)
async def input_new_value_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")
    product_id = data.get("product_id")

    if field is None or product_id is None:
        await message.answer("Ошибка состояния, повторите попытку.")
        await state.clear()
        return

    value = message.text

    # Проверка для цены
    if field == "price":
        try:
            value = float(value)
        except ValueError:
            await message.answer("Введите корректное число для цены.")
            return

    # Получаем текущие изменения или создаём новый словарь
    changed_data = data.get("changed_data", {})
    changed_data[field] = value

    await state.update_data(changed_data=changed_data)
    await state.clear()

    await message.answer(
        f"Значение поля '{field}' обновлено.\n\n"
        "Можете выбрать другое поле для редактирования или сохранить изменения.",
        reply_markup=InlineKeyboards.build_edit_keyboard(product_id)
    )
