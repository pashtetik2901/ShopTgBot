from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.messages import Messages


class Keyboards:

    @staticmethod
    def example_keyboard():
        return ReplyKeyboardMarkup(keyboard=[
            [
                KeyboardButton(text='Текст 1'),
                KeyboardButton(text='Текст 2'),
                KeyboardButton(text=Messages.BUTTON_CONTACT_OPERATOR),

            ]
        ], resize_keyboard=True, one_time_keyboard=False)

    @staticmethod
    def get_reply_keyboard(user_id: int):
        builder = InlineKeyboardBuilder()
        builder.button(text=Messages.BUTTON_ANSWER, callback_data=f"reply_to_dialog_{user_id}")
        builder.button(text=Messages.BUTTON_CANCEL, callback_data=f"cancel_to_dialog_{user_id}")
        return builder.as_markup()
