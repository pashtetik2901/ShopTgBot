from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
    if len(product_list) == 0:
        await message.answer("Нет товаров для редактирования")
        return
    
    # Используем админскую клавиатуру с другим префиксом
    await message.answer(
        "Выберите товар, который нужно редактировать",
        reply_markup=InlineKeyboards.admin_all_product(product_list)  # Используем админский вариант
    )


@redactor_prd_admin.callback_query(F.data.startswith("admin_product_"))  # Изменили здесь
async def select_product_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, _, product_id_str = query.data.split("_", 2)  # admin_product_123 → 3 части
    product_id = int(product_id_str)

    await state.update_data(product_id=product_id, changed_data={})
    await state.set_state(RedactroState.choosing_field)

    await query.message.edit_text(
        "Выберите параметр для редактирования товара:",
        reply_markup=InlineKeyboards.admin_product_detail_keyboard(product_id)
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
            # Используем answer вместо edit_text чтобы избежать ошибки
            await query.message.answer("Нет изменений для сохранения.")
            return

        result = await ProductDAO.refresh_product(product_id, changed_data, session)
        if result:
            # Отправляем новое сообщение вместо редактирования
            await query.message.answer(
                f"Товар успешно обновлен:\n\n"
                f"Название: {result.name}\n"
                f"Описание: {result.description}\n"
                f"Цена: {result.price}\n"
                f"Фото URL: {result.photo_url}"
            )
            await state.clear()
            await state.set_state(StatusState.admin)
        else:
            await query.message.answer("Ошибка при сохранении товара.")
        return

    if action == "cancel":
        # Отправляем новое сообщение вместо редактирования
        await query.message.answer("Редактирование отменено.")
        await state.clear()
        await state.set_state(StatusState.admin)
        return

    # Выбираем поле для редактирования
    field = action
    await state.update_data(field=field, product_id=product_id)

    prompt = {
        "name": "Введите новое название товара",
        "description": "Введите новое описание товара",
        "price": "Введите новую цену товара",
        "photo_url": "Введите новый URL фото товара"
    }.get(field, "Введите новое значение")

    # Отправляем новое сообщение вместо редактирования текущего
    await query.message.answer(prompt)
    await state.set_state(RedactroState.waiting_for_value)
    

@redactor_prd_admin.message(RedactroState.waiting_for_value)
async def input_new_value_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")
    product_id = data.get("product_id")
    changed_data = data.get("changed_data", {})

    if field is None or product_id is None:
        await message.answer("Ошибка состояния, повторите попытку.")
        await state.clear()
        return

    value = message.text

    if field == "price":
        try:
            value = float(value)
        except ValueError:
            await message.answer("Введите корректное число для цены.")
            return

    changed_data[field] = value

    await state.update_data(
        changed_data=changed_data,
        field=None  # Очищаем поле, чтобы не мешало в будущем
    )
    
    await state.set_state(RedactroState.choosing_field)

    await message.answer(
        f"Значение поля '{field}' обновлено.\n\n"
        "Можете выбрать другое поле для редактирования или сохранить изменения.",
        reply_markup=InlineKeyboards.build_edit_keyboard(product_id)
    )